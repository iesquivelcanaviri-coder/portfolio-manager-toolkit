document.addEventListener("DOMContentLoaded", function () { // Waits until the full HTML document has been loaded and parsed before running the JavaScript, which is important because many elements below are selected from the page and would return null if the script ran too early

    // ========================================================= 
    // 1. PAGE ELEMENT REFERENCES // This section stores important HTML elements in variables so they can be reused throughout the script
    // Purpose: // Explains why this section exists
    // - Capture shared elements used across Criteria and Dashboard // These elements are used in more than one feature of the site
    // - Keep all DOM lookups in one place // This improves code organisation and avoids repeating document.getElementById many times
    // ========================================================= 

    const form = document.getElementById("analyze-form"); // Selects the analysis form on the Criteria page; if the user is on another page, this will be null, which is fine because later checks handle that
    const addButton = document.getElementById("add-to-portfolio-btn"); // Selects the button used to add or update an analysed stock in the chosen portfolio
    const portfolioSelect = document.getElementById("portfolio_key"); // Selects the portfolio dropdown so the script can read which portfolio is active and react when it changes
    const tradeMessage = document.getElementById("trade-message"); // Selects the message area used to show info, success, and error feedback to the user
    const marketTable = document.getElementById("market-table"); // Selects the market dashboard table so filtering and sorting logic can be applied only when the table exists

    let latestAnalysis = null; // Creates a variable to store the most recent analysis returned by Flask, which is later reused when the user clicks Add / Update Portfolio

    // =========================================================
    // 2. GENERIC HELPER FUNCTIONS // These are reusable small utility functions used in multiple parts of the script
    // Purpose: // Explains why this block exists
    // - Reusable UI formatting and text update helpers // These functions reduce repeated code and make the main logic easier to read
    // ========================================================= 

    function setText(id, value) { // Creates a helper function that updates text inside an element by its id
        const el = document.getElementById(id); // Looks up the element using the id passed into the function
        if (el) { // Checks that the element actually exists before trying to change it, which prevents runtime errors on pages where that element is missing
            el.textContent = value; // Replaces the visible text inside the element with the new value
        } 
    } 

    function fmtPercent(value) { // Creates a helper function to format decimal values such as 0.125 into percentage strings such as 12.50%
        return value === null || value === undefined || isNaN(value) // Checks whether the value is missing or not a valid number before formatting it
            ? "N/A" // Returns "N/A" if the value is invalid so the UI stays clean and understandable
            : `${(value * 100).toFixed(2)}%`; // Converts the decimal to a percentage, fixes it to 2 decimal places, and adds a percent symbol
    } 

    function fmtNumber(value) { // Creates a helper function to format regular numeric values like beta, Sharpe-like ratio, or price
        return value === null || value === undefined || isNaN(value) // Checks whether the value is invalid before formatting
            ? "N/A" // Returns "N/A" for missing or invalid values
            : Number(value).toFixed(2); // Converts the value into a number and formats it to 2 decimal places for consistent display
    } 

    function parseNumber(value) { // Creates a helper function that safely converts strings into numbers
        const num = parseFloat(value); // Attempts to convert the input value into a floating-point number
        return isNaN(num) ? null : num; // Returns null if conversion fails, otherwise returns the valid number
    } 

    function getSelectedPortfolioName() { // Creates a helper function to get the visible text label of the currently selected portfolio
        if (!portfolioSelect) return "Unknown Portfolio"; // If the portfolio dropdown does not exist on the page, returns a fallback string immediately
        return portfolioSelect.options[portfolioSelect.selectedIndex].text; // Reads the text of the currently selected option from the dropdown, not just the hidden value
    } 

    // ========================================================= 
    // 3. TRADE / STATUS MESSAGE HELPERS // This section controls the feedback messages shown to the user
    // Purpose: // Explains why this block exists
    // - Show success, warning, error, or info messages // These messages help the user understand what happened after an action
    // - Used mainly on the Criteria page // Most of this logic is used after analyse and add-to-portfolio actions
    // ========================================================= 

    function showTradeMessage(message, type = "info") { // Creates a helper function to display a message and assign it a style class such as info, success, or error
        if (!tradeMessage) return; // If the trade message box does not exist on the page, exits early so no error occurs
        tradeMessage.className = `trade-message ${type}`; // Replaces the element's class so CSS can style the message according to the given message type
        tradeMessage.innerHTML = Array.isArray(message) ? message.join("<br>") : message; // If the message is an array, joins all items with line breaks; otherwise displays the single message as HTML
    } 

    function clearTradeMessage() { // Creates a helper function to reset the message box back to an empty neutral state
        if (!tradeMessage) return; // Exits safely if the message element does not exist
        tradeMessage.className = "trade-message"; // Resets the class so info/success/error styling is removed
        tradeMessage.textContent = ""; // Removes any visible message text from the box
    } 

    // ========================================================= 
    // 4. ACCORDION + COLLAPSIBLE HELPERS // This section handles expandable content panels used across the interface
    // Purpose: // Explains why this block exists
    // - Support Position Sizing accordions // These are the expandable sections on the Criteria page
    // - Support portfolio group accordions // These are the expandable sections for grouped current portfolio holdings
    // - Support checklist collapsible panel // This is the collapsible high-level checklist panel
    // ========================================================= 

    function attachAccordion(button) { // Creates a reusable function that attaches accordion open/close behaviour to a given button
        if (!button || button.dataset.bound === "true") { // Stops immediately if the button does not exist or if the script has already attached an event listener to it
            return; // Prevents duplicate event listeners and avoids errors
        } 

        button.dataset.bound = "true"; // Marks the button as already processed by storing a custom data attribute on the element itself

        button.addEventListener("click", function () { // Adds a click event so the button can toggle its related panel
            this.classList.toggle("active"); // Adds or removes the "active" CSS class on the clicked button to visually show open or closed state

            const panel = this.nextElementSibling; // Finds the element immediately after the button, which is assumed to be the content panel connected to that accordion
            if (!panel) return; // Stops if no matching panel is found, which avoids errors if the HTML structure is broken

            panel.style.display = panel.style.display === "block" ? "none" : "block"; // Toggles the panel between visible and hidden by checking its current inline display style
        }); 
    }

    function initialiseStaticAccordions() { // Creates a helper function that finds all accordion buttons already present in the HTML and activates them
        document.querySelectorAll(".accordion").forEach(attachAccordion); // Selects every element with class "accordion" and passes each one into attachAccordion
    }

    function initialiseChecklistCollapsible() { // Creates a helper function to activate the dark checklist collapsible panel
        const buttons = document.querySelectorAll(".collapsible-btn"); // Selects all checklist-style collapsible buttons on the page

        buttons.forEach(button => { // Loops through each collapsible button found
            if (button.dataset.bound === "true") return; // Skips this button if it has already had an event listener attached
            button.dataset.bound = "true"; // Marks this button as already initialised

            button.addEventListener("click", function () { // Adds click behaviour to show or hide the content area directly after the button
                const content = this.nextElementSibling; // Gets the next sibling element, which is expected to be the collapsible content container
                if (!content) return; // Stops safely if the expected content element is missing

                content.style.display = content.style.display === "block" ? "none" : "block"; // Toggles the content visibility by switching display between block and none
            }); 
        });
    } 

    // ========================================================= 
    // 5. CRITERIA PAGE RESET HELPERS // This section resets the analysis output area when needed
    // Purpose: // Explains the role of this block
    // - Clear analysis fields when portfolio changes // Prevents old results from remaining visible after the user switches portfolios
    // - Reset state after failed requests // Keeps the interface clean after errors
    // ========================================================= 

    function clearAnalysisFields() { // Creates a helper function that resets all analysis-related output fields back to default values
        [ // Starts an array containing all HTML ids that display analysis data
            "beta-value", // Span showing beta vs benchmark
            "score-value", // Span showing investment score
            "decision-value", // Span showing decision label
            "weight-value", // Span showing recommended weight
            "sector-value", // Span showing sector
            "industry-value", // Span showing industry
            "tag-value", // Span showing decision tag
            "1y-er-value", // One-year expected return field
            "1y-vol-value", // One-year volatility field
            "1y-sharpe-value", // One-year Sharpe-like field
            "1y-latest-price-value", // One-year latest price field
            "1y-price-start-value", // One-year price start date field
            "1y-price-end-value", // One-year price end date field
            "1y-price-obs-value", // One-year price observations field
            "1y-return-start-value", // One-year return start date field
            "1y-return-end-value", // One-year return end date field
            "1y-return-obs-value", // One-year return observations field
            "1y-quarterly-return-value", // One-year quarterly forecast return field
            "1y-q1-price-value", // One-year forecast Q1 price
            "1y-q2-price-value", // One-year forecast Q2 price
            "1y-q3-price-value", // One-year forecast Q3 price
            "1y-q4-price-value", // One-year forecast Q4 price
            "3m-er-value", // Three-month expected return field
            "3m-vol-value", // Three-month volatility field
            "3m-sharpe-value", // Three-month Sharpe-like field
            "3m-latest-price-value", // Three-month latest price field
            "3m-price-start-value", // Three-month price start date field
            "3m-price-end-value", // Three-month price end date field
            "3m-price-obs-value", // Three-month price observations field
            "3m-return-start-value", // Three-month return start date field
            "3m-return-end-value", // Three-month return end date field
            "3m-return-obs-value", // Three-month return observations field
            "3m-quarterly-return-value", // Three-month quarterly forecast return field
            "3m-q1-price-value", // Three-month forecast Q1 price
            "3m-q2-price-value", // Three-month forecast Q2 price
            "3m-q3-price-value", // Three-month forecast Q3 price
            "3m-q4-price-value", // Three-month forecast Q4 price
            "benchmark-ticker-value", // Benchmark ticker field
            "benchmark-start-value", // Benchmark start date field
            "benchmark-end-value", // Benchmark end date field
            "beta-obs-value" // Beta observation count field
        ].forEach(id => setText(id, "N/A")); // Loops through every id above and resets the visible text to "N/A" using the helper function

        setText("result-ticker", "Select a stock to analyze"); // Resets the main result heading to its default instructional message
        setText("portfolio-name", getSelectedPortfolioName()); // Updates the visible portfolio name to match the current dropdown selection

        if (addButton) { // Checks that the add/update button exists before changing it
            addButton.disabled = true; // Disables the Add / Update Portfolio button until a fresh successful analysis is completed
        }

        latestAnalysis = null; // Clears the stored analysis payload so outdated analysis cannot be added to a portfolio accidentally
        clearTradeMessage(); // Removes any old success or error message from the interface
    } 

    if (portfolioSelect) { // Only attaches the change event if the portfolio dropdown exists on the current page
        portfolioSelect.addEventListener("change", function () { // Listens for portfolio selection changes
            clearAnalysisFields(); // Clears all displayed analysis outputs because a new portfolio context means old results may no longer be valid
            setText("portfolio-name", getSelectedPortfolioName()); // Updates the visible portfolio name immediately after the user changes the dropdown
        }); 
    } 

    // ========================================================= 
    // 6. CURRENT PORTFOLIO HOLDINGS RENDERING // This section draws the grouped stored positions on the page
    // Purpose: // Explains why this exists
    // - Build grouped holdings by portfolio // The backend sends grouped portfolio data and this function converts it into visible HTML
    // - Show summary metrics per portfolio // Each group shows positions, allocation, remaining cash, and average beta
    // - Show current stored positions // Users can see which tickers are already inside each portfolio
    // ========================================================= 

    function renderPortfolioGroups(grouped) { // Creates a function that receives grouped portfolio data from Flask and renders it into the page
        const container = document.getElementById("portfolio-groups"); // Selects the empty container where the grouped portfolio sections should be inserted
        if (!container) return; // Exits safely if the page does not include the portfolio groups container

        container.innerHTML = ""; // Clears any previous portfolio group HTML so the new render starts from a clean state

        Object.entries(grouped).forEach(([, data]) => { // Loops through each portfolio entry in the grouped object; the key is ignored here and only the data object is used
            const button = document.createElement("button"); // Creates a new button element that will act as the accordion header for this portfolio
            button.className = "accordion portfolio-group-button"; // Assigns CSS classes so the button looks like the other accordions and can be styled consistently
            button.type = "button"; // Explicitly sets button type so it does not accidentally behave like a submit button inside any surrounding form
            button.textContent = data.portfolio_name; // Uses the portfolio's display name as the visible accordion title

            const panel = document.createElement("div"); // Creates the content container that will open underneath the accordion button
            panel.className = "panel"; // Assigns the panel class so it receives accordion panel styling from CSS

            const summary = data.summary || {}; // Reads the summary object for this portfolio, or uses an empty object if summary data is missing

            const summaryBox = document.createElement("div"); // Creates a wrapper for summary statistics
            summaryBox.className = "portfolio-summary"; // Assigns the summary box class so CSS Grid styling can lay the items out nicely
            summaryBox.innerHTML = ` // Inserts multiple summary lines using a template literal so dynamic values can be embedded directly
                <p><strong>Positions:</strong> ${summary.position_count ?? 0}</p> // Shows the number of positions, defaulting to 0 if missing
                <p><strong>Total Allocated:</strong> ${summary.total_allocated_percent ?? 0}%</p> // Shows the total allocated percentage, defaulting to 0
                <p><strong>Remaining Cash:</strong> ${summary.remaining_cash_percent ?? 100}%</p> // Shows the remaining cash percentage, defaulting to 100
                <p><strong>Average Beta:</strong> ${summary.average_beta ?? "N/A"}</p> // Shows the portfolio average beta, or N/A if unavailable
            `; // Ends the summary HTML template
            panel.appendChild(summaryBox); // Adds the summary box inside the accordion panel before the holdings table or empty message

            if (!data.stocks || data.stocks.length === 0) { // Checks whether this portfolio currently has no stored stocks
                const empty = document.createElement("p"); // Creates a paragraph element for the empty-state message
                empty.textContent = "No stocks added yet."; // Sets the empty-state message text
                panel.appendChild(empty); // Adds the empty-state message into the panel
            } else { // Runs this block if the portfolio has one or more stored stocks
                const table = document.createElement("table"); // Creates a table element to display the stored positions
                table.className = "table";  // Assigns the shared table class so the holdings table uses the site's table styling

                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Recommended Weight</th>
                            <th>Decision</th>
                            <th>Tag</th>
                            <th>Sector</th>
                            <th>Industry</th>
                            <th>Beta</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.stocks.map(stock => `
                            <tr>
                                <td>${stock.ticker}</td>
                                <td>${stock.recommended_weight}</td>
                                <td>${stock.decision}</td>
                                <td>${stock.tag}</td>
                                <td>${stock.sector || "Unknown"}</td>
                                <td>${stock.industry || "Unknown"}</td>
                                <td>${stock.beta !== null && stock.beta !== undefined ? Number(stock.beta).toFixed(2) : "N/A"}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                `;
                panel.appendChild(table); // Adds the completed holdings table inside the panel
            } 

            container.appendChild(button); // Inserts the accordion button into the portfolio groups container
            container.appendChild(panel); // Inserts the panel immediately after the button so the accordion logic can find it using nextElementSibling
            attachAccordion(button); // Activates accordion behaviour on the new button that was created dynamically with JavaScript
        }); 
    } 

    async function loadPortfolioGroups() { // Creates an async function that fetches stored portfolio holdings from Flask and displays them
        const container = document.getElementById("portfolio-groups"); // Selects the container where holdings should appear
        if (!container) return; // Exits if the current page does not contain that container

        try { // Starts a try block to handle network request errors cleanly
            const res = await fetch("/portfolio-stocks"); // Sends a GET request to the Flask endpoint that returns grouped portfolio holdings as JSON
            const data = await res.json(); // Converts the response body into a JavaScript object
            renderPortfolioGroups(data); // Passes the returned data into the rendering function so the UI is updated
        } catch (error) { // Catches fetch or parsing errors
            console.error("Failed to load portfolio groups:", error); // Writes a helpful debugging message into the browser console
        } 
    }

    // ========================================================= 
    // 7. CRITERIA PAGE: ANALYSE TICKER SUBMISSION // This section handles the analysis form submission
    // Purpose: // Explains why this exists
    // - Submit portfolio + ticker to Flask // Sends the user's selected portfolio and ticker to the backend for analysis
    // - Populate all analysis result sections // Fills the UI with the response returned by Flask
    // ========================================================= 

    if (form) { // Only adds the submit logic if the analysis form exists on the current page
        form.addEventListener("submit", async function (e) { // Listens for form submission and handles it with async logic
            e.preventDefault(); // Stops the browser from doing a normal page reload form submission because the script wants to handle it with fetch instead
            clearTradeMessage(); // Clears any old message before starting a new analysis request

            const formData = new FormData(form); // Builds a FormData object from the form fields so it can be sent to Flask exactly like a normal form post

            try { // Starts a try block for the async request
                const res = await fetch("/analyze", { // Sends the analysis request to the Flask /analyze route
                    method: "POST", // Uses POST because data is being submitted to the server
                    body: formData, // Sends the form fields in the request body
                    headers: { "X-Requested-With": "XMLHttpRequest" } // Adds a header often used to indicate that the request was made asynchronously with JavaScript
                }); 

                const data = await res.json(); // Converts the JSON response into a JavaScript object

                if (!res.ok || data.error) { // Checks whether the server returned an HTTP error or an application-level error message
                    clearAnalysisFields(); // Resets all result fields so failed analysis does not leave misleading previous data on the page
                    setText("result-ticker", "Analysis Error"); // Changes the result heading to show that something went wrong
                    setText("decision-value", data.error || "Could not load analysis."); // Displays the specific error if available, otherwise a general fallback message
                    showTradeMessage(data.error || "Could not load analysis.", "error"); // Shows a visible red error message to the user
                    return; // Stops the function so no further UI population is attempted
                } 

                latestAnalysis = data; // Stores the successful analysis payload so it can later be reused by the Add / Update Portfolio button

                if (addButton) { // Checks whether the add button exists on the page
                    addButton.disabled = false; // Enables the Add / Update Portfolio button now that a valid analysis exists
                } 

                // ------------------------------------------------- 
                // 7.1 Summary section // This block fills the top summary fields in the result box
                // ------------------------------------------------- 
                setText("result-ticker", `${data.ticker} — Analysis Summary`); // Updates the main result heading with the analysed ticker symbol
                setText("portfolio-name", data.portfolio_name || getSelectedPortfolioName()); // Displays the portfolio name returned by Flask, or falls back to the selected dropdown text
                setText("beta-value", data.beta === null ? "N/A" : fmtNumber(data.beta)); // Displays formatted beta if available, otherwise N/A
                setText("score-value", data.score ?? "N/A"); // Displays the score or N/A if missing
                setText("decision-value", data.decision || "N/A"); // Displays the decision label or N/A
                setText("weight-value", data.recommended_weight || "N/A"); // Displays the recommended weight or N/A
                setText("sector-value", data.sector || "Unknown"); // Displays sector with a fallback if missing
                setText("industry-value", data.industry || "Unknown"); // Displays industry with a fallback if missing
                setText("tag-value", data.tag || "N/A"); // Displays decision tag or N/A

                // ------------------------------------------------- 
                // 7.2 One-year historical analysis // This block fills the 1-year metrics section
                // ------------------------------------------------- 
                if (data.one_year) { // Only fills this section if the one_year object exists in the Flask response
                    setText("1y-er-value", fmtPercent(data.one_year.annualised_expected_return)); // Formats and displays annualised expected return as a percentage
                    setText("1y-vol-value", fmtPercent(data.one_year.annualised_volatility)); // Formats and displays annualised volatility as a percentage
                    setText("1y-sharpe-value", fmtNumber(data.one_year.sharpe_like)); // Displays the Sharpe-like ratio as a regular number
                    setText("1y-latest-price-value", fmtNumber(data.one_year.latest_price)); // Displays the latest price to 2 decimal places
                    setText("1y-price-start-value", data.one_year.price_start_date || "N/A"); // Displays the first date in the price series
                    setText("1y-price-end-value", data.one_year.price_end_date || "N/A"); // Displays the last date in the price series
                    setText("1y-price-obs-value", data.one_year.price_observations ?? "N/A"); // Displays the number of price observations
                    setText("1y-return-start-value", data.one_year.return_start_date || "N/A"); // Displays the first date in the return series
                    setText("1y-return-end-value", data.one_year.return_end_date || "N/A"); // Displays the last date in the return series
                    setText("1y-return-obs-value", data.one_year.return_observations ?? "N/A"); // Displays the number of return observations

                    if (data.one_year.forecast) { // Only fills forecast fields if the one_year forecast object exists
                        setText("1y-quarterly-return-value", fmtPercent(data.one_year.forecast.quarterly_return)); // Displays the quarterly expected return used in the simplified forecast
                        setText("1y-q1-price-value", fmtNumber(data.one_year.forecast.q1_expected_price)); // Displays Q1 expected price
                        setText("1y-q2-price-value", fmtNumber(data.one_year.forecast.q2_expected_price)); // Displays Q2 expected price
                        setText("1y-q3-price-value", fmtNumber(data.one_year.forecast.q3_expected_price)); // Displays Q3 expected price
                        setText("1y-q4-price-value", fmtNumber(data.one_year.forecast.q4_expected_price)); // Displays Q4 expected price
                    } 
                } 

                // -------------------------------------------------
                // 7.3 Three-month historical analysis // This block fills the 3-month metrics section
                // -------------------------------------------------
                if (data.three_month) { // Only fills this section if the three_month object exists
                    setText("3m-er-value", fmtPercent(data.three_month.annualised_expected_return)); // Displays three-month annualised expected return
                    setText("3m-vol-value", fmtPercent(data.three_month.annualised_volatility)); // Displays three-month annualised volatility
                    setText("3m-sharpe-value", fmtNumber(data.three_month.sharpe_like)); // Displays three-month Sharpe-like ratio
                    setText("3m-latest-price-value", fmtNumber(data.three_month.latest_price)); // Displays latest price from the three-month window
                    setText("3m-price-start-value", data.three_month.price_start_date || "N/A"); // Displays three-month price start date
                    setText("3m-price-end-value", data.three_month.price_end_date || "N/A"); // Displays three-month price end date
                    setText("3m-price-obs-value", data.three_month.price_observations ?? "N/A"); // Displays number of price observations
                    setText("3m-return-start-value", data.three_month.return_start_date || "N/A"); // Displays three-month return start date
                    setText("3m-return-end-value", data.three_month.return_end_date || "N/A"); // Displays three-month return end date
                    setText("3m-return-obs-value", data.three_month.return_observations ?? "N/A"); // Displays number of return observations

                    if (data.three_month.forecast) { // Only fills three-month forecast fields if the forecast object exists
                        setText("3m-quarterly-return-value", fmtPercent(data.three_month.forecast.quarterly_return)); // Displays quarterly expected return derived from the three-month window
                        setText("3m-q1-price-value", fmtNumber(data.three_month.forecast.q1_expected_price)); // Displays Q1 forecast price
                        setText("3m-q2-price-value", fmtNumber(data.three_month.forecast.q2_expected_price)); // Displays Q2 forecast price
                        setText("3m-q3-price-value", fmtNumber(data.three_month.forecast.q3_expected_price)); // Displays Q3 forecast price
                        setText("3m-q4-price-value", fmtNumber(data.three_month.forecast.q4_expected_price)); // Displays Q4 forecast price
                    } 
                } 

                // ------------------------------------------------- 
                // 7.4 Benchmark section // This block fills the benchmark-related fields
                // ------------------------------------------------- 
                setText("benchmark-ticker-value", data.benchmark_ticker || "N/A"); // Displays the benchmark ticker used for beta calculation
                setText("benchmark-start-value", data.benchmark_start_date || "N/A"); // Displays benchmark return series start date
                setText("benchmark-end-value", data.benchmark_end_date || "N/A"); // Displays benchmark return series end date
                setText("beta-obs-value", data.beta_observations ?? "N/A"); // Displays the number of overlapping observations used to calculate beta

                showTradeMessage( // Calls the message helper to show a final info note after successful analysis
                    "Analysis completed. Review mandate fit before adding to portfolio.", // The user-facing message
                    "info" // Message type so the CSS info styling is applied
                ); // Ends showTradeMessage call
            } catch (error) { // Catches network errors, JSON parsing errors, or other unexpected failures during the request
                clearAnalysisFields(); // Resets the result box to a clean state
                setText("result-ticker", "Request Failed"); // Updates the heading to indicate that the request failed technically
                setText("decision-value", "Could not load analysis."); // Shows a fallback failure message in the decision field
                showTradeMessage("Could not load analysis.", "error"); // Shows a visible red error message
                console.error(error); // Logs the raw error object to the browser console for debugging
            } 
        }); 
    } 

    // ========================================================= 
    // 8. CRITERIA PAGE: ADD / UPDATE PORTFOLIO POSITION // This section handles saving the analysed stock into the selected portfolio
    // Purpose: // Explains why this exists
    // - Add analysed security to selected portfolio // Saves new positions
    // - Update existing position if same ticker already exists // Prevents duplicate holdings by replacing matching tickers
    // - Refresh grouped holdings // Updates the visible holdings panel immediately after saving
    // ========================================================= 

    if (addButton) { // Only attaches this logic if the Add / Update Portfolio button exists on the page
        addButton.addEventListener("click", async function () { // Listens for clicks on the button and handles them asynchronously
            if (!latestAnalysis) return; // Stops immediately if there is no saved analysis object, which prevents adding empty or outdated data

            const selectedPortfolioKey = portfolioSelect // Starts choosing the portfolio key to send to Flask
                ? portfolioSelect.value // Uses the currently selected dropdown value if the dropdown exists
                : latestAnalysis.portfolio_key; // Otherwise falls back to the portfolio key stored inside the analysis result

            const selectedPortfolioName = getSelectedPortfolioName(); // Reads the visible name of the selected portfolio for display and storage purposes

            try { // Starts a try block for the POST request
                const res = await fetch("/add-to-portfolio", { // Sends a request to the Flask endpoint that validates and stores the position
                    method: "POST", // Uses POST because new data is being sent to the server
                    headers: { // Starts the request headers object
                        "Content-Type": "application/json" // Tells Flask the request body is JSON, not form data
                    }, // Ends headers object
                    body: JSON.stringify({ // Converts the JavaScript object below into a JSON string for the request body
                        ticker: latestAnalysis.ticker, // Sends the analysed ticker
                        portfolio_key: selectedPortfolioKey, // Sends the selected portfolio key
                        portfolio_name: selectedPortfolioName, // Sends the visible portfolio name
                        recommended_weight: latestAnalysis.recommended_weight, // Sends the recommended weight from the analysis
                        decision: latestAnalysis.decision, // Sends the decision label
                        tag: latestAnalysis.tag, // Sends the decision tag
                        sector: latestAnalysis.sector, // Sends sector for storage and later display
                        industry: latestAnalysis.industry, // Sends industry for storage and later display
                        beta: latestAnalysis.beta // Sends beta value for storage and later display
                    }) 
                });

                const data = await res.json(); // Converts the JSON response into a JavaScript object

                if (!res.ok || data.error) { // Checks whether the server returned an error status or an application-level validation error
                    const errors = Array.isArray(data.error) // Checks whether the backend sent one error or an array of errors
                        ? data.error // Uses the backend error array directly if it is already an array
                        : [data.error || "Failed to add stock."]; // Otherwise wraps the error in an array, or uses a generic fallback message

                    const warnings = Array.isArray(data.warnings) // Checks whether warnings were returned as an array
                        ? data.warnings // Uses the warnings array if it exists
                        : []; // Otherwise falls back to an empty warnings array

                    showTradeMessage([...errors, ...warnings], "error"); // Merges errors and warnings into one array and shows them in the message box as an error-style message
                    return; // Stops the function so no success logic runs
                } 

                renderPortfolioGroups(data.portfolio); // Re-renders the grouped holdings area using the updated portfolio data returned by Flask

                const messages = [data.message || "Portfolio updated."]; // Starts an array with the main success message returned by the server, or a fallback if missing
                if (Array.isArray(data.warnings) && data.warnings.length > 0) { // Checks whether the backend also returned warnings alongside the successful update
                    messages.push(...data.warnings); // Appends all warnings to the success message list
                } 

                showTradeMessage(messages, "success"); // Shows a success message box containing the main message and any warnings
            } catch (error) { // Catches network or parsing errors during the add/update request
                showTradeMessage("Failed to add to portfolio.", "error"); // Displays a visible error message to the user
                console.error("Failed to add to portfolio:", error); // Logs the technical error in the browser console for debugging
            }
        }); 
    } 

    // =========================================================
    // 9. MARKET DASHBOARD: FILTERS, PRESETS, SORTING // This section handles all interactive behaviour for the Market Dashboard page
    // Purpose: // Explains why this exists
    // - Provide portfolio-manager style screening workflow // Lets the user narrow the investment universe quickly
    // - Enable manual filters + quick preset screens // Supports both flexible custom filtering and one-click preset views
    // - Support column sorting // Allows the user to reorder the table by clicking headers
    // =========================================================

    function initialiseMarketDashboard() { // Creates the main setup function for the dashboard page
        if (!marketTable) return; // Stops immediately if the market table does not exist, which prevents dashboard code from running on other pages

        const tbody = marketTable.querySelector("tbody"); // Selects the table body because filtering and sorting are applied to the data rows inside it
        const headers = marketTable.querySelectorAll("th[data-sort]"); // Selects only sortable table headers, identified by the custom data-sort attribute

        // -----------------------------------------------------
        // 9.1 Filter controls // This block selects the manual filter inputs
        // -----------------------------------------------------
        const tickerFilter = document.getElementById("ticker-filter"); // Dropdown for ticker filtering
        const sectorFilter = document.getElementById("sector-filter"); // Dropdown for sector filtering
        const decisionFilter = document.getElementById("decision-filter"); // Dropdown for decision filtering
        const scoreFilter = document.getElementById("score-filter"); // Dropdown for minimum score filtering
        const betaFilter = document.getElementById("beta-filter"); // Numeric input for maximum beta
        const volatilityFilter = document.getElementById("volatility-filter"); // Numeric input for maximum volatility
        const sharpeFilter = document.getElementById("sharpe-filter"); // Numeric input for minimum Sharpe-like ratio
        const peFilter = document.getElementById("pe-filter"); // Numeric input for maximum P/E ratio
        const summary = document.getElementById("dashboard-summary"); // Paragraph used to display summary text after filters are applied

        // -----------------------------------------------------
        // 9.2 Preset buttons // This block selects the one-click preset filter buttons
        // -----------------------------------------------------
        const presetLowRisk = document.getElementById("preset-low-risk"); // Button for low-risk preset
        const presetHighConviction = document.getElementById("preset-high-conviction"); // Button for high-conviction preset
        const presetCore = document.getElementById("preset-core"); // Button for core holdings preset
        const presetSatellite = document.getElementById("preset-satellite"); // Button for satellite preset
        const presetExploratory = document.getElementById("preset-exploratory"); // Button for exploratory preset
        const presetIncome = document.getElementById("preset-income"); // Button for income/defensive preset
        const presetBestRanked = document.getElementById("preset-best-ranked"); // Button for best-ranked preset
        const presetCash = document.getElementById("preset-cash"); // Button for cash preset
        const clearFiltersBtn = document.getElementById("clear-filters"); // Button used to reset all filters back to default state
        let activePreset = ""; // Stores the currently selected preset name so the filter engine knows which preset logic to apply

        // ----------------------------------------------------- 
        // 9.3 Apply all dashboard filters // This block contains the main filter engine
        // ----------------------------------------------------- 
        function applyDashboardFilters() { // Creates the function that reads all current filter values and shows/hides rows accordingly
            const rows = tbody.querySelectorAll("tr"); // Selects all table rows currently inside the dashboard table body

            const tickerValue = tickerFilter ? tickerFilter.value.toUpperCase() : ""; // Reads ticker filter value and normalises it to uppercase so comparison is consistent with ticker symbols
            const sectorValue = sectorFilter ? sectorFilter.value : ""; // Reads sector filter value
            const decisionValue = decisionFilter ? decisionFilter.value : ""; // Reads decision filter value
            const scoreValue = scoreFilter ? parseNumber(scoreFilter.value) : null; // Reads minimum score filter and converts it safely to a number
            const betaValue = betaFilter ? parseNumber(betaFilter.value) : null; // Reads maximum beta filter and converts it safely to a number
            const volatilityValue = volatilityFilter ? parseNumber(volatilityFilter.value) : null; // Reads maximum volatility filter as a number
            const sharpeValue = sharpeFilter ? parseNumber(sharpeFilter.value) : null; // Reads minimum Sharpe filter as a number
            const peValue = peFilter ? parseNumber(peFilter.value) : null; // Reads maximum P/E filter as a number

            let visibleCount = 0; // Creates a counter to track how many rows remain visible after filtering

            rows.forEach(row => { // Loops through every row in the dashboard table
                const rowTicker = (row.dataset.ticker || "").toUpperCase(); // Reads the row's custom data-ticker attribute and converts it to uppercase for matching
                const rowSector = row.dataset.sector || ""; // Reads the row's sector from its data attribute
                const rowDecision = row.dataset.decision || ""; // Reads the row's decision from its data attribute
                const rowScore = parseNumber(row.dataset.score); // Reads and parses the row score
                const rowBeta = parseNumber(row.dataset.beta); // Reads and parses the row beta
                const rowVolatility = parseNumber(row.dataset.volatility); // Reads and parses the row volatility
                const rowSharpe = parseNumber(row.dataset.sharpe); // Reads and parses the row Sharpe-like ratio
                const rowPE = parseNumber(row.dataset.pe); // Reads and parses the row P/E ratio

                const rowIsLowRisk = row.dataset.lowRisk === "true"; // Converts the row's low-risk flag from string to boolean
                const rowIsHighConviction = row.dataset.highConviction === "true"; // Converts the row's high-conviction flag from string to boolean
                const rowIsCoreHolding = row.dataset.coreHolding === "true"; // Converts the row's core-holding flag from string to boolean
                const rowIsSatellite = row.dataset.satellite === "true"; // Converts the row's satellite flag from string to boolean
                const rowIsExploratory = row.dataset.exploratory === "true"; // Converts the row's exploratory flag from string to boolean
                const rowIsCashCandidate = row.dataset.cashCandidate === "true"; // Converts the row's cash-candidate flag from string to boolean
                const rowIsIncomeCandidate = row.dataset.incomeCandidate === "true"; // Converts the row's income-candidate flag from string to boolean
                const rowIsBestRanked = row.dataset.bestRanked === "true"; // Converts the row's best-ranked flag from string to boolean

                let visible = true; // Starts by assuming each row should be visible, then switches to false if any filter rule fails

                if (tickerValue && rowTicker !== tickerValue) { // If a ticker filter is selected and the current row ticker does not match it exactly
                    visible = false; // Hide the row
                }
                if (sectorValue && rowSector !== sectorValue) { // If a sector filter is selected and the row sector does not match
                    visible = false; // Hide the row
                }
                if (decisionValue && rowDecision !== decisionValue) { // If a decision filter is selected and the row decision does not match
                    visible = false; // Hide the row
                } 
                if (scoreValue !== null && (rowScore === null || rowScore < scoreValue)) { // If a minimum score is set and the row score is missing or too low
                    visible = false; // Hide the row
                } 
                if (betaValue !== null && (rowBeta === null || rowBeta > betaValue)) { // If a maximum beta is set and the row beta is missing or higher than allowed
                    visible = false; // Hide the row
                } 
                if (volatilityValue !== null && (rowVolatility === null || rowVolatility > volatilityValue)) { // If a maximum volatility is set and the row is missing volatility or exceeds the threshold
                    visible = false; // Hide the row
                } 
                if (sharpeValue !== null && (rowSharpe === null || rowSharpe < sharpeValue)) { // If a minimum Sharpe is set and the row is missing it or is below threshold
                    visible = false; // Hide the row
                } 
                if (peValue !== null && (rowPE === null || rowPE > peValue)) { // If a maximum P/E is set and the row is missing it or is above threshold
                    visible = false; // Hide the row
                } 
                if (activePreset === "low-risk" && !rowIsLowRisk) { // If the low-risk preset is active and the row is not flagged as low-risk
                    visible = false; // Hide the row
                }
                if (activePreset === "high-conviction" && !rowIsHighConviction) { // If the high-conviction preset is active and the row is not flagged accordingly
                    visible = false; // Hide the row
                }
                if (activePreset === "core" && !rowIsCoreHolding) { // If the core preset is active and the row is not marked as a core holding
                    visible = false; // Hide the row
                }
                if (activePreset === "satellite" && !rowIsSatellite) { // If the satellite preset is active and the row is not marked as satellite
                    visible = false; // Hide the row
                }
                if (activePreset === "exploratory" && !rowIsExploratory) { // If the exploratory preset is active and the row is not flagged exploratory
                    visible = false; // Hide the row
                }
                if (activePreset === "cash" && !rowIsCashCandidate) { // If the cash preset is active and the row is not flagged as a cash candidate
                    visible = false; // Hide the row
                }
                if (activePreset === "income" && !rowIsIncomeCandidate) { // If the income preset is active and the row is not flagged income/defensive
                    visible = false; // Hide the row
                }
                if (activePreset === "best-ranked" && !rowIsBestRanked) { // If the best-ranked preset is active and the row is not flagged as best-ranked
                    visible = false; // Hide the row
                }

                row.style.display = visible ? "" : "none"; // Shows the row normally if visible stays true, otherwise hides it by setting display to none

                if (visible) { // Checks whether the row remained visible after all rules were applied
                    visibleCount += 1; // Increments the counter of visible rows
                }
            }); 

            if (summary) { // Only updates summary text if the summary element exists on the page
                let summaryText = `Showing ${visibleCount} securities after applying filters.`; // Sets the default summary message using the visible row count

                if (activePreset === "low-risk") { // Checks whether the low-risk preset is currently active
                    summaryText = `Showing ${visibleCount} low-risk securities. Filter logic: beta at or below 1 and moderate volatility.`; // Replaces summary with a low-risk explanation
                } else if (activePreset === "high-conviction") { // Checks whether the high-conviction preset is active
                    summaryText = `Showing ${visibleCount} high-conviction securities. Filter logic: names classified as YES — high conviction with score 7 or above.`; // Replaces summary accordingly
                } else if (activePreset === "core") { // Checks whether the core preset is active
                    summaryText = `Showing ${visibleCount} core holdings. Filter logic: names classified as YES — core holding.`; // Replaces summary accordingly
                } else if (activePreset === "satellite") { // Checks whether the satellite preset is active
                    summaryText = `Showing ${visibleCount} satellite / diversifier positions. Filter logic: names classified as YES — satellite.`; // Replaces summary accordingly
                } else if (activePreset === "exploratory") { // Checks whether the exploratory preset is active
                    summaryText = `Showing ${visibleCount} exploratory / high-risk positions. Filter logic: names classified as LIMITED — high risk / exploratory.`; // Replaces summary accordingly
                } else if (activePreset === "income") { // Checks whether the income preset is active
                    summaryText = `Showing ${visibleCount} income / defensive securities. Filter logic: dividend-paying names or defensive / bond-style instruments flagged by the model.`; // Replaces summary accordingly
                } else if (activePreset === "best-ranked") { // Checks whether the best-ranked preset is active
                    summaryText = `Showing ${visibleCount} best-ranked securities. Filter logic: score 5 or above and Sharpe-like ratio of at least 0.3.`; // Replaces summary accordingly
                } else if (activePreset === "cash") { // Checks whether the cash preset is active
                    summaryText = `Showing ${visibleCount} cash / risk-control names. Filter logic: names classified as NO — hold as cash instead.`; // Replaces summary accordingly
                } 

                summary.textContent = summaryText; // Writes the chosen summary text into the dashboard summary paragraph
            } 
        } 

        // ----------------------------------------------------- // Visual subsection divider
        // 9.4 Reset all dashboard filters // This block clears all filter controls
        // ----------------------------------------------------- // End subsection divider
        function clearDashboardFilters() { // Creates a helper function that resets all dashboard filters to their default state
            if (tickerFilter) tickerFilter.value = ""; // Clears ticker dropdown selection if it exists
            if (sectorFilter) sectorFilter.value = ""; // Clears sector dropdown selection if it exists
            if (decisionFilter) decisionFilter.value = ""; // Clears decision dropdown selection if it exists
            if (scoreFilter) scoreFilter.value = ""; // Clears minimum score dropdown if it exists
            if (betaFilter) betaFilter.value = ""; // Clears maximum beta input if it exists
            if (volatilityFilter) volatilityFilter.value = ""; // Clears maximum volatility input if it exists
            if (sharpeFilter) sharpeFilter.value = ""; // Clears minimum Sharpe input if it exists
            if (peFilter) peFilter.value = ""; // Clears maximum P/E input if it exists

            activePreset = ""; // Clears the stored preset name so no preset-specific filtering remains active
            applyDashboardFilters(); // Re-runs the filter engine so the table updates immediately to the reset state
        } 

        // ----------------------------------------------------- // Visual subsection divider
        // 9.5 Preset screens for faster PM workflow // This block wires up the one-click preset buttons
        // ----------------------------------------------------- // End subsection divider
        if (presetLowRisk) { // Only attaches this event if the low-risk button exists
            presetLowRisk.addEventListener("click", function () { // Runs when the user clicks the Low Risk preset button
                clearDashboardFilters(); // Resets all existing filters first so presets start from a clean state
                activePreset = "low-risk"; // Stores the active preset name
                applyDashboardFilters(); // Applies the preset filtering immediately
            }); 
        } 

        if (presetHighConviction) { // Only attaches this event if the high-conviction button exists
            presetHighConviction.addEventListener("click", function () { // Runs when the High Conviction button is clicked
                clearDashboardFilters(); // Clears old filter state first
                activePreset = "high-conviction"; // Sets the active preset flag
                applyDashboardFilters(); // Applies the preset filtering
            }); 
        } 

        if (presetCore) { // Only attaches this event if the core button exists
            presetCore.addEventListener("click", function () { // Runs when the Core Holdings button is clicked
                clearDashboardFilters(); // Resets all manual filters first
                activePreset = "core"; // Sets active preset to core
                applyDashboardFilters(); // Applies filtering
            }); 
        } 

        if (presetSatellite) { // Only attaches this event if the satellite button exists
            presetSatellite.addEventListener("click", function () { // Runs when the Satellite button is clicked
                clearDashboardFilters(); // Resets all other filters
                activePreset = "satellite"; // Stores current preset name
                applyDashboardFilters(); // Applies filtering
            }); 
        }

        if (presetExploratory) { // Only attaches this event if the exploratory button exists
            presetExploratory.addEventListener("click", function () { // Runs when the Exploratory button is clicked
                clearDashboardFilters(); // Clears all old filter state
                activePreset = "exploratory"; // Sets active preset
                applyDashboardFilters(); // Applies filtering
            }); 
        } 

        if (presetIncome) { // Only attaches this event if the income button exists
            presetIncome.addEventListener("click", function () { // Runs when the Income / Defensive button is clicked
                clearDashboardFilters(); // Clears all filters first
                activePreset = "income"; // Sets active preset
                applyDashboardFilters(); // Applies filtering
            }); 
        } 

        if (presetBestRanked) { // Only attaches this event if the best-ranked button exists
            presetBestRanked.addEventListener("click", function () { // Runs when the Best Ranked button is clicked
                clearDashboardFilters(); // Clears all filters first
                activePreset = "best-ranked"; // Sets active preset
                applyDashboardFilters(); // Applies filtering
            }); 
        } 

        if (presetCash) { // Only attaches this event if the cash button exists
            presetCash.addEventListener("click", function () { // Runs when the Cash button is clicked
                clearDashboardFilters(); // Clears all filters first
                activePreset = "cash"; // Sets active preset
                applyDashboardFilters(); // Applies filtering
            });
        } 

        if (clearFiltersBtn) { // Only attaches this event if the Clear Filters button exists
            clearFiltersBtn.addEventListener("click", clearDashboardFilters); // Makes the button run the filter reset helper when clicked
        } 

        // ----------------------------------------------------- 
        // 9.6 Bind manual filter controls // This block makes manual filter fields trigger filtering
        // Important: // Notes why the logic below behaves as it does
        // - Any manual filter removes preset mode // This avoids mixing manual and preset logic in confusing ways
        // - This avoids conflicting logic // Keeps the screening behaviour easier to understand and debug
        // ----------------------------------------------------- 
        [ // Starts an array containing all filter controls that should trigger filtering when changed
            tickerFilter, // Ticker dropdown
            sectorFilter, // Sector dropdown
            decisionFilter, // Decision dropdown
            scoreFilter, // Score dropdown
            betaFilter, // Beta input
            volatilityFilter, // Volatility input
            sharpeFilter, // Sharpe input
            peFilter // P/E input
        ].forEach(control => { // Loops through each control in the filter array
            if (control) { // Only attaches events if the control actually exists
                control.addEventListener("input", function () { // Reacts live as the user types into number fields or changes some controls
                    activePreset = ""; // Clears any active preset because manual filtering now takes priority
                    applyDashboardFilters(); // Re-runs the filter engine immediately
                }); 

                control.addEventListener("change", function () { // Reacts to change events, especially useful for dropdowns
                    activePreset = ""; // Clears any active preset
                    applyDashboardFilters(); // Re-runs the filter engine
                }); 
            }
        }); 

        // ----------------------------------------------------- 
        // 9.7 Table sorting // This block enables clickable column sorting
        // ----------------------------------------------------- 
        function getCellValue(row, index) { // Creates a helper function to read the text from a specific cell position inside a row
            return row.children[index].textContent.trim(); // Returns the trimmed visible text from the cell at the given column index
        } // Ends getCellValue

        headers.forEach((header, index) => { // Loops through each sortable table header and keeps track of its column index
            header.style.cursor = "pointer"; // Adds pointer cursor so users can see the header is clickable
            header.dataset.direction = "desc"; // Stores a default sort direction on each header using a custom data attribute

            header.addEventListener("click", function () { // Runs whenever the user clicks a sortable column header
                const rows = Array.from(tbody.querySelectorAll("tr")); // Converts all current table rows into a real array so they can be sorted with JavaScript
                const direction = this.dataset.direction === "asc" ? "desc" : "asc"; // Toggles the sort direction each time the same header is clicked
                this.dataset.direction = direction; // Saves the new direction back onto the clicked header

                rows.sort((a, b) => { // Sorts the row array using a custom comparison function
                    const aText = getCellValue(a, index); // Reads the text from the current column for row a
                    const bText = getCellValue(b, index); // Reads the text from the current column for row b

                    const aNum = parseFloat(aText.replace(/[^\d.-]/g, "")); // Attempts to extract a numeric value from the cell text by removing symbols like % and commas; this is a harder line because it lets one sorting function handle both plain numbers and formatted numeric strings
                    const bNum = parseFloat(bText.replace(/[^\d.-]/g, "")); // Does the same numeric extraction for row b

                    let comparison; // Creates a variable to store the comparison result
                    if (!isNaN(aNum) && !isNaN(bNum)) { // If both extracted values are valid numbers
                        comparison = aNum - bNum; // Sort numerically by subtracting one from the other
                    } else { // If one or both values are not valid numbers
                        comparison = aText.localeCompare(bText); // Sort alphabetically using localeCompare, which handles string comparison more cleanly than plain > or <
                    } 

                    return direction === "asc" ? comparison : -comparison; // Returns normal comparison for ascending order, or reverses it for descending order
                });

                rows.forEach(row => tbody.appendChild(row)); // Re-appends each sorted row into the tbody in the new order, which updates the visible table
                applyDashboardFilters(); // Re-applies filters after sorting so hidden rows stay hidden and visible rows stay counted correctly
            }); 
        }); 

        applyDashboardFilters(); // Runs the filter engine once when the dashboard first loads so the summary text and row visibility are initialised correctly
    }

    // ========================================================= 
    // 10. INITIAL PAGE LOAD // This final section activates the relevant features when the page is ready
    // Purpose: // Explains why this block exists
    // - Activate static UI behaviours // Turns on accordions and collapsible panels
    // - Load saved portfolio groups // Fetches existing stored holdings from Flask
    // - Activate dashboard tools if current page has the table // Only runs dashboard filtering/sorting where needed
    // ========================================================= 
    initialiseStaticAccordions(); // Activates any accordion sections already written in the HTML
    initialiseChecklistCollapsible(); // Activates the collapsible checklist button and panel
    initialiseMarketDashboard(); // Activates dashboard filtering and sorting logic if the market table exists on the current page
    loadPortfolioGroups(); // Fetches stored grouped portfolio holdings and renders them if the holdings container exists

});