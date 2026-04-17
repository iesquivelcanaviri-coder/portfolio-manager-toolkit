document.addEventListener("DOMContentLoaded", function () { // Waits until the full HTML document has been loaded and parsed before running the JavaScript, which is important because many elements below are selected from the page and would return null if the script ran too early

    // =========================================================
    // SHARED SECTION → PAGE DETECTION + COMMON ELEMENT REFERENCES
    // Purpose:
    // - Detect which HTML page is currently loaded
    // - Capture shared elements used across multiple pages
    // - Keep all DOM lookups in one place
    // =========================================================

    const body = document.body; // Stores the body element so page-level checks can be performed if needed
    const form = document.getElementById("analyze-form"); // Selects the analysis form on the Criteria page; if the user is on another page, this will be null, which is fine because later checks handle that
    const addButton = document.getElementById("add-to-portfolio-btn"); // Selects the button used to add or update an analysed stock in the chosen portfolio
    const portfolioSelect = document.getElementById("portfolio_key"); // Selects the portfolio dropdown so the script can read which portfolio is active and react when it changes
    const tradeMessage = document.getElementById("trade-message"); // Selects the message area used to show info, success, and error feedback to the user
    const marketTable = document.getElementById("market-table"); // Selects the market dashboard table so filtering and sorting logic can be applied only when the table exists
    const tickerSelect = document.getElementById("ticker"); // Selects the ticker dropdown used on the Criteria page
    const portfolioGroupsContainer = document.getElementById("portfolio-groups"); // Selects the container that shows grouped portfolio holdings on the Criteria page

    let latestAnalysis = null; // Creates a variable to store the most recent analysis returned by Flask, which is later reused when the user clicks Add / Update Portfolio

    // =========================================================
    // SHARED SECTION → TICKER UNIVERSE
    // Purpose:
    // - Provide the full ticker universe for dropdown population
    // - Reuse the same universe used conceptually in the dashboard
    // =========================================================

    const tickerUniverse = { // Creates a grouped ticker object so the Criteria dropdown can be populated dynamically with all available securities
        fixed_income: [ // Starts the fixed-income category used for bond and bond-like ETFs
            "SHY", "IEF", "TLT", "BND", "AGG", "TIP", "LQD", "HYG", "VGIT", "VCIT",
            "MINT", "BIL", "JPST", "SCHR", "SCHZ", "IGIB", "SPTI", "GOVT", "BSV", "VGSH"
        ], 
        defensive_equities: [ // Starts the defensive-equities category used for more stable stocks and ETFs
            "XLP", "XLV", "XLU", "PG", "KO", "PEP", "JNJ", "MRK", "PFE",
            "WMT", "MCD", "CL", "KMB", "DUK", "SO", "NEE", "GIS", "MDT", "HSY", "EL"
        ], 
        core_equities: [ // Starts the core-equities category used for large-cap core holdings
            "AAPL", "MSFT", "AMZN", "GOOGL", "META", "JPM", "V", "MA", "UNH",
            "HD", "ADBE", "CRM", "ORCL", "CSCO", "INTU", "AVGO", "NFLX",
            "QCOM", "LIN", "TXN", "HON", "CAT", "IBM", "AMGN", "NOW", "BKNG",
            "AXP", "GS", "BLK", "SPGI"
        ], 
        growth_equities: [ // Starts the growth-equities category used for higher-growth names and ETFs
            "TSLA", "NVDA", "AMD", "SHOP", "SQ", "UBER", "PANW", "CRWD", "SNOW", "PLTR",
            "MDB", "DDOG", "NET", "ZS", "TEAM", "ABNB", "MELI", "SE", "TTD", "ROKU",
            "ARKK", "QQQ", "SMH", "SOXX", "IWF", "VUG", "XLK", "FTEC", "SCHG", "MGK"
        ], 
        international_equities: [ // Starts the international-equities category used for geographic diversification
            "VEA", "IEFA", "EWG", "EWQ", "EWI", "EWJ", "EWS", "EWA", "EWU", "EWP",
            "VGK", "EZU", "FEZ", "AAXJ", "VWO", "EEM", "INDA", "EWY", "MCHI", "FXI",
            "EWZ", "EWT", "EIDO", "EPHE", "EZA", "ERUS", "EWC", "EWL", "EWD", "EWN"
        ], 
        alternatives: [ // Starts the alternatives category used for non-traditional exposures
            "GLD", "SLV", "VNQ", "REET", "SCHH", "REM", "DBC", "PDBC", "USO", "IAU",
            "VNQI", "RWO", "FTGC", "COMT", "GSG", "DBA", "UUP", "FXE", "FXF", "FXY",
            "BITO", "ETHE", "PALL", "PLTM", "URA", "COPX", "WOOD", "HACK", "CIBR", "KWEB"
        ] 
    }; 

    // =========================================================
    // SHARED SECTION → GENERIC HELPER FUNCTIONS
    // Purpose:
    // - Reusable UI formatting and text update helpers
    // - Reduce repeated code and keep the main logic easier to read
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
    // SHARED SECTION → TRADE / STATUS MESSAGE HELPERS
    // Purpose:
    // - Show success, warning, error, or info messages
    // - Used mainly on the Criteria page
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
    // SHARED SECTION → ACCORDION + COLLAPSIBLE HELPERS
    // Purpose:
    // - Support Position Sizing accordions
    // - Support portfolio group accordions
    // - Support checklist collapsible panel
    // =========================================================

    function attachAccordion(button) { // Creates a reusable function that attaches accordion open/close behaviour to a given button
        if (!button || button.dataset.bound === "true") { // Stops immediately if the button does not exist or if the script has already attached an event listener to it
            return; // Prevents duplicate event listeners and avoids errors
        } // Ends the guard clause

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
    // INDEX.HTML SECTION
    // Purpose:
    // - Keep a dedicated place for index page logic
    // - Easy to expand later if homepage interactivity is added
    // =========================================================

    function initialiseIndexPage() { // Creates an initialiser for the homepage so index-specific logic can be added cleanly later
        const isIndexPage = window.location.pathname === "/" || window.location.pathname.endsWith("index.html"); // Checks whether the current page is the homepage
        if (!isIndexPage) return; // Stops immediately if the current page is not the homepage

        
    } 

    // =========================================================
    // PORTFOLIO_PROFILES.HTML SECTION
    // Purpose:
    // - Keep a dedicated place for portfolio profiles page logic
    // - Easy to expand later if profile accordions or filters are added
    // =========================================================

    function initialisePortfolioProfilesPage() { // Creates an initialiser for the portfolio profiles page so logic stays grouped by HTML file
        const isPortfolioProfilesPage = window.location.pathname.includes("portfolio_profiles"); // Checks whether the current page is the portfolio profiles page
        if (!isPortfolioProfilesPage) return; // Stops immediately if the current page is not portfolio_profiles.html

      
    } 

    // =========================================================
    // CONTACT.HTML SECTION
    // Purpose:
    // - Keep a dedicated place for contact page logic
    // - Easy to expand later if contact form validation is added
    // =========================================================

    function initialiseContactPage() { // Creates an initialiser for the contact page so contact-specific logic can be added later in a clean section
        const isContactPage = window.location.pathname.includes("contact"); // Checks whether the current page is the contact page
        if (!isContactPage) return; // Stops immediately if the current page is not contact.html

    } 

    // =========================================================
    // CRITERIA.HTML SECTION → TICKER DROPDOWN POPULATION
    // Purpose:
    // - Populate the ticker dropdown dynamically
    // - Replace the old hardcoded 3-ticker list
    // - Group tickers by category for better readability
    // =========================================================

    function populateTickerDropdown() { // Creates a helper function that builds the full ticker dropdown dynamically from the grouped ticker universe
        if (!tickerSelect) return; // Stops immediately if the ticker dropdown does not exist on the current page

        tickerSelect.innerHTML = ""; // Clears any existing hardcoded or previously inserted options so the dropdown can be rebuilt cleanly

        const placeholder = document.createElement("option"); // Creates a placeholder option so the user is prompted to choose a ticker
        placeholder.value = ""; // Sets placeholder value to empty so validation can still require a real ticker
        placeholder.textContent = "-- Choose a ticker --"; // Sets the visible placeholder text shown to the user
        placeholder.selected = true; // Makes the placeholder the default selected option
        placeholder.disabled = false; // Leaves the placeholder enabled so the user can still see it at the top of the dropdown
        tickerSelect.appendChild(placeholder); // Adds the placeholder option into the dropdown before grouped ticker options

        Object.entries(tickerUniverse).forEach(([category, tickers]) => { // Loops through each category and its ticker array inside the grouped ticker universe
            const optgroup = document.createElement("optgroup"); // Creates an optgroup element so tickers can be visually grouped by category inside the select dropdown
            optgroup.label = category.replace(/_/g, " ").replace(/\b\w/g, char => char.toUpperCase()); // Converts category keys such as fixed_income into cleaner labels such as Fixed Income

            tickers.forEach(ticker => { // Loops through every ticker inside the current category
                const option = document.createElement("option"); // Creates one option element for one ticker
                option.value = ticker; // Stores the raw ticker symbol as the submitted form value
                option.textContent = ticker; // Shows the ticker symbol as the dropdown display text
                optgroup.appendChild(option); // Adds the ticker option inside the current category group
            }); // Ends loop through tickers in one category

            tickerSelect.appendChild(optgroup); // Adds the completed category group into the select dropdown
        }); 
    } 

    // =========================================================
    // CRITERIA.HTML SECTION → RESET HELPERS
    // Purpose:
    // - Clear analysis fields when portfolio changes
    // - Reset state after failed requests
    // =========================================================

    function clearAnalysisFields() { // Creates a helper function that resets all analysis-related output fields back to default values
        [ // Starts an array containing all HTML ids that display analysis data
            "beta-value",
            "score-value",
            "decision-value",
            "weight-value",
            "sector-value",
            "industry-value",
            "tag-value",
            "1y-er-value",
            "1y-vol-value",
            "1y-sharpe-value",
            "1y-latest-price-value",
            "1y-price-start-value",
            "1y-price-end-value",
            "1y-price-obs-value",
            "1y-return-start-value",
            "1y-return-end-value",
            "1y-return-obs-value",
            "1y-quarterly-return-value",
            "1y-q1-price-value",
            "1y-q2-price-value",
            "1y-q3-price-value",
            "1y-q4-price-value",
            "3m-er-value",
            "3m-vol-value",
            "3m-sharpe-value",
            "3m-latest-price-value",
            "3m-price-start-value",
            "3m-price-end-value",
            "3m-price-obs-value",
            "3m-return-start-value",
            "3m-return-end-value",
            "3m-return-obs-value",
            "3m-quarterly-return-value",
            "3m-q1-price-value",
            "3m-q2-price-value",
            "3m-q3-price-value",
            "3m-q4-price-value",
            "benchmark-ticker-value",
            "benchmark-start-value",
            "benchmark-end-value",
            "beta-obs-value"
        ].forEach(id => setText(id, "N/A")); // Loops through every id above and resets the visible text to "N/A" using the helper function

        setText("result-ticker", "Select a stock to analyze"); // Resets the main result heading to its default instructional message
        setText("portfolio-name", getSelectedPortfolioName()); // Updates the visible portfolio name to match the current dropdown selection

        if (addButton) { // Checks that the add/update button exists before changing it
            addButton.disabled = true; // Disables the Add / Update Portfolio button until a fresh successful analysis is completed
        } 

        latestAnalysis = null; // Clears the stored analysis payload so outdated analysis cannot be added to a portfolio accidentally
        clearTradeMessage(); // Removes any old success or error message from the interface
    } 

    // =========================================================
    // CRITERIA.HTML SECTION → CURRENT PORTFOLIO HOLDINGS RENDERING
    // Purpose:
    // - Build grouped holdings by portfolio
    // - Show summary metrics per portfolio
    // - Show current stored positions
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
            summaryBox.innerHTML = `
                <p><strong>Positions:</strong> ${summary.position_count ?? 0}</p>
                <p><strong>Total Allocated:</strong> ${summary.total_allocated_percent ?? 0}%</p>
                <p><strong>Remaining Cash:</strong> ${summary.remaining_cash_percent ?? 100}%</p>
                <p><strong>Average Beta:</strong> ${summary.average_beta ?? "N/A"}</p>
            `; 
            panel.appendChild(summaryBox); // Adds the summary box inside the accordion panel before the holdings table or empty message

            if (!data.stocks || data.stocks.length === 0) { // Checks whether this portfolio currently has no stored stocks
                const empty = document.createElement("p"); // Creates a paragraph element for the empty-state message
                empty.textContent = "No stocks added yet."; // Sets the empty-state message text
                panel.appendChild(empty); // Adds the empty-state message into the panel
            } else { // Runs this block if the portfolio has one or more stored stocks
                const table = document.createElement("table"); // Creates a table element to display the stored positions
                table.className = "table"; // Assigns the shared table class so the holdings table uses the site's table styling

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
    // CRITERIA.HTML SECTION → ANALYSE TICKER SUBMISSION
    // Purpose:
    // - Submit portfolio + ticker to Flask
    // - Populate all analysis result sections
    // =========================================================

    function initialiseCriteriaAnalysisForm() { // Creates a dedicated initialiser for the Criteria page analysis form so Criteria logic stays grouped together
        if (!form) return; // Stops immediately if the analysis form does not exist on the current page

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

                setText("result-ticker", `${data.ticker} — Analysis Summary`); // Updates the main result heading with the analysed ticker symbol
                setText("portfolio-name", data.portfolio_name || getSelectedPortfolioName()); // Displays the portfolio name returned by Flask, or falls back to the selected dropdown text
                setText("beta-value", data.beta === null ? "N/A" : fmtNumber(data.beta)); // Displays formatted beta if available, otherwise N/A
                setText("score-value", data.score ?? "N/A"); // Displays the score or N/A if missing
                setText("decision-value", data.decision || "N/A"); // Displays the decision label or N/A
                setText("weight-value", data.recommended_weight || "N/A"); // Displays the recommended weight or N/A
                setText("sector-value", data.sector || "Unknown"); // Displays sector with a fallback if missing
                setText("industry-value", data.industry || "Unknown"); // Displays industry with a fallback if missing
                setText("tag-value", data.tag || "N/A"); // Displays decision tag or N/A

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

                setText("benchmark-ticker-value", data.benchmark_ticker || "N/A"); // Displays the benchmark ticker used for beta calculation
                setText("benchmark-start-value", data.benchmark_start_date || "N/A"); // Displays benchmark return series start date
                setText("benchmark-end-value", data.benchmark_end_date || "N/A"); // Displays benchmark return series end date
                setText("beta-obs-value", data.beta_observations ?? "N/A"); // Displays the number of overlapping observations used to calculate beta

                showTradeMessage("Analysis completed. Review mandate fit before adding to portfolio.", "info"); // Calls the message helper to show a final info note after successful analysis
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
    // CRITERIA.HTML SECTION → ADD / UPDATE PORTFOLIO POSITION
    // Purpose:
    // - Add analysed security to selected portfolio
    // - Update existing position if same ticker already exists
    // - Refresh grouped holdings
    // =========================================================
    function initialiseCriteriaAddToPortfolio() { // Creates a dedicated initialiser for the Add / Update Portfolio button so Criteria page save logic stays grouped together
        if (!addButton) return; // Stops immediately if the Add / Update Portfolio button does not exist on the current page

        addButton.addEventListener("click", async function () { // Listens for clicks on the button and handles them asynchronously
            if (!latestAnalysis) return; // Stops immediately if there is no saved analysis object, which prevents adding empty or outdated data

            const selectedPortfolioKey = portfolioSelect ? portfolioSelect.value : latestAnalysis.portfolio_key; // Uses the currently selected portfolio key if the dropdown exists, otherwise falls back to the key stored in the analysis result
            const selectedPortfolioName = getSelectedPortfolioName(); // Reads the visible name of the selected portfolio for display and storage purposes

            try { // Starts a try block for the POST request
                const res = await fetch("/add-to-portfolio", { // Sends a request to the Flask endpoint that validates and stores the position
                    method: "POST", // Uses POST because new data is being sent to the server
                    headers: { "Content-Type": "application/json" }, // Tells Flask the request body is JSON, not form data
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
                    const errors = Array.isArray(data.error) ? data.error : [data.error || "Failed to add stock."]; // Converts backend error response into a normalised array
                    const warnings = Array.isArray(data.warnings) ? data.warnings : []; // Converts backend warnings into a safe array
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

    function initialiseCriteriaPage() { // Creates the main Criteria page initialiser so all Criteria-specific logic can be run from one place
        const isCriteriaPage = window.location.pathname.includes("criteria"); // Checks whether the current page is the Criteria page
        if (!isCriteriaPage) return; // Stops immediately if the current page is not criteria.html

        populateTickerDropdown(); // Populates the ticker dropdown with the full grouped ticker universe
        initialiseCriteriaAnalysisForm(); // Activates async analysis form submission logic
        initialiseCriteriaAddToPortfolio(); // Activates add/update portfolio button logic
        loadPortfolioGroups(); // Loads grouped portfolio holdings into the Criteria page if the container exists

        if (portfolioSelect) { // Only attaches the change event if the portfolio dropdown exists on the current page
            portfolioSelect.addEventListener("change", function () { // Listens for portfolio selection changes
                clearAnalysisFields(); // Clears all displayed analysis outputs because a new portfolio context means old results may no longer be valid
                setText("portfolio-name", getSelectedPortfolioName()); // Updates the visible portfolio name immediately after the user changes the dropdown
            }); 
        } 
    } 

    // =========================================================
    // MARKET_DASHBOARD.HTML SECTION
    // Purpose:
    // - Provide portfolio-manager style screening workflow
    // - Enable manual filters + quick preset screens
    // - Support column sorting
    // =========================================================

    function initialiseMarketDashboard() { // Creates the main setup function for the dashboard page
        if (!marketTable) return; // Stops immediately if the market table does not exist, which prevents dashboard code from running on other pages

        const tbody = marketTable.querySelector("tbody"); // Selects the table body because filtering and sorting are applied to the data rows inside it
        const headers = marketTable.querySelectorAll("th[data-sort]"); // Selects only sortable table headers, identified by the custom data-sort attribute

        const tickerFilter = document.getElementById("ticker-filter"); // Dropdown for ticker filtering
        const decisionFilter = document.getElementById("decision-filter"); // Dropdown for decision filtering
        const scoreFilter = document.getElementById("score-filter"); // Dropdown for minimum score filtering
        const volatilityFilter = document.getElementById("volatility-filter"); // Numeric input for maximum volatility
        const sharpeFilter = document.getElementById("sharpe-filter"); // Numeric input for minimum Sharpe
        const summary = document.getElementById("dashboard-summary"); // Paragraph used to display summary text after filters are applied

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

        function applyDashboardFilters() { // Creates the function that reads all current filter values and shows/hides rows accordingly
            const rows = tbody.querySelectorAll("tr"); // Selects all table rows currently inside the dashboard table body

            const tickerValue = tickerFilter ? tickerFilter.value.toUpperCase() : ""; // Reads ticker filter value and normalises it to uppercase
            const decisionValue = decisionFilter ? decisionFilter.value : ""; // Reads decision filter value
            const scoreValue = scoreFilter ? parseNumber(scoreFilter.value) : null; // Reads minimum score filter and converts it safely to a number
            const volatilityValue = volatilityFilter ? parseNumber(volatilityFilter.value) : null; // Reads maximum volatility filter as a number
            const sharpeValue = sharpeFilter ? parseNumber(sharpeFilter.value) : null; // Reads minimum Sharpe filter as a number

            let visibleCount = 0; // Creates a counter to track how many rows remain visible after filtering

            rows.forEach(row => { // Loops through every row in the dashboard table
                const rowTicker = (row.dataset.ticker || "").toUpperCase(); // Reads the row ticker
                const rowDecision = row.dataset.decision || ""; // Reads the row decision
                const rowScore = parseNumber(row.dataset.score); // Reads and parses the row score
                const rowVolatility = parseNumber(row.dataset.volatility); // Reads and parses the row volatility
                const rowSharpe = parseNumber(row.dataset.sharpe); // Reads and parses the row Sharpe-like ratio

                const rowIsLowRisk = row.dataset.lowRisk === "true"; // Converts the row's low-risk flag from string to boolean
                const rowIsHighConviction = row.dataset.highConviction === "true"; // Converts the row's high-conviction flag from string to boolean
                const rowIsCoreHolding = row.dataset.coreHolding === "true"; // Converts the row's core-holding flag from string to boolean
                const rowIsSatellite = row.dataset.satellite === "true"; // Converts the row's satellite flag from string to boolean
                const rowIsExploratory = row.dataset.exploratory === "true"; // Converts the row's exploratory flag from string to boolean
                const rowIsCashCandidate = row.dataset.cashCandidate === "true"; // Converts the row's cash-candidate flag from string to boolean
                const rowIsIncomeCandidate = row.dataset.incomeCandidate === "true"; // Converts the row's income-candidate flag from string to boolean
                const rowIsBestRanked = row.dataset.bestRanked === "true"; // Converts the row's best-ranked flag from string to boolean

                let visible = true; // Starts by assuming each row should be visible

                if (tickerValue && rowTicker !== tickerValue) visible = false; // Hides row when ticker does not match selected ticker filter
                if (decisionValue && rowDecision !== decisionValue) visible = false; // Hides row when decision does not match selected decision filter
                if (scoreValue !== null && (rowScore === null || rowScore < scoreValue)) visible = false; // Hides row when score is missing or too low
                if (volatilityValue !== null && (rowVolatility === null || rowVolatility > volatilityValue)) visible = false; // Hides row when volatility is missing or too high
                if (sharpeValue !== null && (rowSharpe === null || rowSharpe < sharpeValue)) visible = false; // Hides row when Sharpe is missing or too low

                if (activePreset === "low-risk" && !rowIsLowRisk) visible = false; // Hides row when low-risk preset is active and the row is not low-risk
                if (activePreset === "high-conviction" && !rowIsHighConviction) visible = false; // Hides row when high-conviction preset is active and the row is not high conviction
                if (activePreset === "core" && !rowIsCoreHolding) visible = false; // Hides row when core preset is active and the row is not a core holding
                if (activePreset === "satellite" && !rowIsSatellite) visible = false; // Hides row when satellite preset is active and the row is not a satellite
                if (activePreset === "exploratory" && !rowIsExploratory) visible = false; // Hides row when exploratory preset is active and the row is not exploratory
                if (activePreset === "cash" && !rowIsCashCandidate) visible = false; // Hides row when cash preset is active and the row is not a cash candidate
                if (activePreset === "income" && !rowIsIncomeCandidate) visible = false; // Hides row when income preset is active and the row is not an income candidate
                if (activePreset === "best-ranked" && !rowIsBestRanked) visible = false; // Hides row when best-ranked preset is active and the row is not best-ranked

                row.style.display = visible ? "" : "none"; // Shows or hides the row

                if (visible) visibleCount += 1; // Increments visible row count
            });

            if (summary) { // Only updates summary text if the summary element exists on the page
                let summaryText = `Showing ${visibleCount} securities after applying filters.`; // Default summary message

                if (activePreset === "low-risk") summaryText = `Showing ${visibleCount} low-risk securities. Filter logic: lower-volatility names that passed the model.`; // Summary for low-risk preset
                else if (activePreset === "high-conviction") summaryText = `Showing ${visibleCount} high-conviction securities. Filter logic: names classified as YES — high conviction with score 7 or above.`; // Summary for high-conviction preset
                else if (activePreset === "core") summaryText = `Showing ${visibleCount} core holdings. Filter logic: names classified as YES — core holding.`; // Summary for core preset
                else if (activePreset === "satellite") summaryText = `Showing ${visibleCount} satellite / diversifier positions. Filter logic: names classified as YES — satellite.`; // Summary for satellite preset
                else if (activePreset === "exploratory") summaryText = `Showing ${visibleCount} exploratory / high-risk positions. Filter logic: names classified as LIMITED — high risk / exploratory.`; // Summary for exploratory preset
                else if (activePreset === "income") summaryText = `Showing ${visibleCount} income / defensive securities. Filter logic: defensive or bond-style instruments flagged by the model.`; // Summary for income preset
                else if (activePreset === "best-ranked") summaryText = `Showing ${visibleCount} best-ranked securities. Filter logic: score 5 or above and Sharpe-like ratio of at least 0.3.`; // Summary for best-ranked preset
                else if (activePreset === "cash") summaryText = `Showing ${visibleCount} cash / risk-control names. Filter logic: names classified as NO — hold as cash instead.`; // Summary for cash preset

                summary.textContent = summaryText; // Updates summary paragraph
            }
        }

        function clearDashboardFilters() { // Creates a helper function that resets all dashboard filters to their default state
            if (tickerFilter) tickerFilter.value = "";
            if (decisionFilter) decisionFilter.value = "";
            if (scoreFilter) scoreFilter.value = "";
            if (volatilityFilter) volatilityFilter.value = "";
            if (sharpeFilter) sharpeFilter.value = "";

            activePreset = ""; // Clears preset mode
            applyDashboardFilters(); // Re-runs filtering after reset
        }

        if (presetLowRisk) presetLowRisk.addEventListener("click", function () { clearDashboardFilters(); activePreset = "low-risk"; applyDashboardFilters(); });
        if (presetHighConviction) presetHighConviction.addEventListener("click", function () { clearDashboardFilters(); activePreset = "high-conviction"; applyDashboardFilters(); });
        if (presetCore) presetCore.addEventListener("click", function () { clearDashboardFilters(); activePreset = "core"; applyDashboardFilters(); });
        if (presetSatellite) presetSatellite.addEventListener("click", function () { clearDashboardFilters(); activePreset = "satellite"; applyDashboardFilters(); });
        if (presetExploratory) presetExploratory.addEventListener("click", function () { clearDashboardFilters(); activePreset = "exploratory"; applyDashboardFilters(); });
        if (presetIncome) presetIncome.addEventListener("click", function () { clearDashboardFilters(); activePreset = "income"; applyDashboardFilters(); });
        if (presetBestRanked) presetBestRanked.addEventListener("click", function () { clearDashboardFilters(); activePreset = "best-ranked"; applyDashboardFilters(); });
        if (presetCash) presetCash.addEventListener("click", function () { clearDashboardFilters(); activePreset = "cash"; applyDashboardFilters(); });
        if (clearFiltersBtn) clearFiltersBtn.addEventListener("click", clearDashboardFilters);

        [tickerFilter, decisionFilter, scoreFilter, volatilityFilter, sharpeFilter].forEach(control => {
            if (control) {
                control.addEventListener("input", function () {
                    activePreset = "";
                    applyDashboardFilters();
                });

                control.addEventListener("change", function () {
                    activePreset = "";
                    applyDashboardFilters();
                });
            }
        });

        function getCellValue(row, index) { // Creates a helper function to read the text from a specific cell position inside a row
            return row.children[index].textContent.trim(); // Returns the trimmed visible text from the cell at the given column index
        }

        headers.forEach((header, index) => { // Loops through each sortable table header and keeps track of its column index
            header.style.cursor = "pointer"; // Adds pointer cursor so users can see the header is clickable
            header.dataset.direction = "desc"; // Stores a default sort direction on each header

            header.addEventListener("click", function () { // Runs whenever the user clicks a sortable column header
                const rows = Array.from(tbody.querySelectorAll("tr")); // Converts current table rows into an array
                const direction = this.dataset.direction === "asc" ? "desc" : "asc"; // Toggles sort direction
                this.dataset.direction = direction; // Saves new direction

                rows.sort((a, b) => { // Sorts rows
                    const aText = getCellValue(a, index); // Cell text from row a
                    const bText = getCellValue(b, index); // Cell text from row b

                    const aNum = parseFloat(aText.replace(/[^\d.-]/g, "")); // Tries to extract numeric value
                    const bNum = parseFloat(bText.replace(/[^\d.-]/g, "")); // Tries to extract numeric value

                    let comparison; // Stores comparison result
                    if (!isNaN(aNum) && !isNaN(bNum)) comparison = aNum - bNum; // Numeric sort
                    else comparison = aText.localeCompare(bText); // Alphabetic sort

                    return direction === "asc" ? comparison : -comparison; // Applies chosen sort direction
                });

                rows.forEach(row => tbody.appendChild(row)); // Rebuilds table body in sorted order
                applyDashboardFilters(); // Reapplies filters after sorting
            });
        });

        applyDashboardFilters(); // Runs filter logic once on page load
    }
    // =========================================================
    // INITIAL PAGE LOAD
    // Purpose:
    // - Activate shared UI behaviours
    // - Activate page-specific logic by HTML file
    // =========================================================
    initialiseStaticAccordions(); // Activates any accordion sections already written in the HTML
    initialiseChecklistCollapsible(); // Activates the collapsible checklist button and panel
    initialiseIndexPage(); // Activates any future index.html-specific logic
    initialisePortfolioProfilesPage(); // Activates any future portfolio_profiles.html-specific logic
    initialiseCriteriaPage(); // Activates all criteria.html-specific logic
    initialiseMarketDashboard(); // Activates all market_dashboard.html-specific logic
    initialiseContactPage(); // Activates any future contact.html-specific logic

}); 