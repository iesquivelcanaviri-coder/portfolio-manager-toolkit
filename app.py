document.addEventListener("DOMContentLoaded", function () { // Waits until the full HTML document has been loaded and parsed before running the JavaScript, which is important because many elements below are selected from the page and would return null if the script ran too early

// =========================================================
// SHARED SECTION → PAGE CHECK + COMMON ELEMENTS
// This block collects the main HTML elements that are reused
// across different pages, so I do not have to keep selecting
// them again and again later in the file.
// =========================================================

const body = document.body; // keeping a reference to the whole page in case I need page-level checks later
const form = document.getElementById("analyze-form"); // this is the analysis form on criteria.html
const addButton = document.getElementById("add-to-portfolio-btn"); // button used to add or update a stock in a portfolio
const portfolioSelect = document.getElementById("portfolio_key"); // dropdown that lets the user choose which portfolio they are working with
const tradeMessage = document.getElementById("trade-message"); // area where success, warning, or error messages are shown
const marketTable = document.getElementById("market-table"); // main table used on the market dashboard page
const tickerSelect = document.getElementById("ticker"); // ticker dropdown on the criteria page
const portfolioGroupsContainer = document.getElementById("portfolio-groups"); // area where grouped portfolio holdings are displayed

let latestAnalysis = null; // I use this to store the latest stock analysis result so it can be reused when adding to the portfolio


// =========================================================
// SHARED SECTION → TICKER UNIVERSE
// This is the full list of tickers grouped by type.
// I use it to build the dropdown dynamically instead of
// hardcoding only a few names in the HTML.
// =========================================================

const tickerUniverse = { // grouped ticker list so the dropdown is cleaner and easier to scan
    fixed_income: [ // bond and bond-like ETFs
        "SHY", "IEF", "TLT", "BND", "AGG", "TIP", "LQD", "HYG", "VGIT", "VCIT",
        "MINT", "BIL", "JPST", "SCHR", "SCHZ", "IGIB", "SPTI", "GOVT", "BSV", "VGSH"
    ],
    defensive_equities: [ // lower-risk or more defensive shares and ETFs
        "XLP", "XLV", "XLU", "PG", "KO", "PEP", "JNJ", "MRK", "PFE",
        "WMT", "MCD", "CL", "KMB", "DUK", "SO", "NEE", "GIS", "MDT", "HSY", "EL"
    ],
    core_equities: [ // larger core holdings that would often sit in a main portfolio
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "JPM", "V", "MA", "UNH",
        "HD", "ADBE", "CRM", "ORCL", "CSCO", "INTU", "AVGO", "NFLX",
        "QCOM", "LIN", "TXN", "HON", "CAT", "IBM", "AMGN", "NOW", "BKNG",
        "AXP", "GS", "BLK", "SPGI"
    ],
    growth_equities: [ // higher-growth names, usually more volatile
        "TSLA", "NVDA", "AMD", "SHOP", "SQ", "UBER", "PANW", "CRWD", "SNOW", "PLTR",
        "MDB", "DDOG", "NET", "ZS", "TEAM", "ABNB", "MELI", "SE", "TTD", "ROKU",
        "ARKK", "QQQ", "SMH", "SOXX", "IWF", "VUG", "XLK", "FTEC", "SCHG", "MGK"
    ],
    international_equities: [ // international and regional exposure for diversification
        "VEA", "IEFA", "EWG", "EWQ", "EWI", "EWJ", "EWS", "EWA", "EWU", "EWP",
        "VGK", "EZU", "FEZ", "AAXJ", "VWO", "EEM", "INDA", "EWY", "MCHI", "FXI",
        "EWZ", "EWT", "EIDO", "EPHE", "EZA", "ERUS", "EWC", "EWL", "EWD", "EWN"
    ],
    alternatives: [ // non-traditional exposures like commodities, real assets, crypto-linked products, etc.
        "GLD", "SLV", "VNQ", "REET", "SCHH", "REM", "DBC", "PDBC", "USO", "IAU",
        "VNQI", "RWO", "FTGC", "COMT", "GSG", "DBA", "UUP", "FXE", "FXF", "FXY",
        "BITO", "ETHE", "PALL", "PLTM", "URA", "COPX", "WOOD", "HACK", "CIBR", "KWEB"
    ]
};


// =========================================================
// SHARED SECTION → SMALL HELPER FUNCTIONS
// These are utility functions I can reuse in different places
// so the main logic stays cleaner and easier to understand.
// =========================================================

function setText(id, value) { // quick helper to update text in one element by id
    const el = document.getElementById(id); // first I look for the element
    if (el) { // only update it if it actually exists on that page
        el.textContent = value; // then replace its visible text
    }
}

function fmtPercent(value) { // used when I want decimals like 0.125 to display as 12.50%
    return value === null || value === undefined || isNaN(value)
        ? "N/A" // keeps the screen clean if the value is missing or invalid
        : `${(value * 100).toFixed(2)}%`; // converts decimal to percent and keeps formatting consistent
}

function fmtNumber(value) { // used for things like beta, price, or Sharpe-like values
    return value === null || value === undefined || isNaN(value)
        ? "N/A"
        : Number(value).toFixed(2); // forces a neat 2-decimal format across the UI
}

function parseNumber(value) { // safely turns text input into a real number
    const num = parseFloat(value); // parseFloat is useful because many inputs arrive as strings
    return isNaN(num) ? null : num; // null is easier to test later than NaN
}

function getSelectedPortfolioName() { // gets the visible label from the portfolio dropdown
    if (!portfolioSelect) return "Unknown Portfolio"; // safe fallback in case the dropdown is not on the page
    return portfolioSelect.options[portfolioSelect.selectedIndex].text; // returns the text the user sees, not just the hidden value
}


// =========================================================
// SHARED SECTION → MESSAGE BOX HELPERS
// These are mostly for the criteria page, where the user needs
// feedback after analysing or adding a stock.
// =========================================================

function showTradeMessage(message, type = "info") { // shows one message or a list of messages with a style like info/success/error
    if (!tradeMessage) return; // if the message box is not on the page, just stop quietly
    tradeMessage.className = `trade-message ${type}`; // swaps the class so CSS can colour it correctly
    tradeMessage.innerHTML = Array.isArray(message) ? message.join("<br>") : message; // if there are multiple messages, show each on a new line
}

function clearTradeMessage() { // resets the message box back to blank
    if (!tradeMessage) return;
    tradeMessage.className = "trade-message"; // removes any success/error/info styling
    tradeMessage.textContent = ""; // clears the visible text
}


// =========================================================
// SHARED SECTION → ACCORDION / COLLAPSIBLE LOGIC
// This is reused in places where content needs to open and close,
// like portfolio sections or checklist panels.
// =========================================================

function attachAccordion(button) { // gives one accordion button its open/close behaviour
    if (!button || button.dataset.bound === "true") { // avoids errors and also stops duplicate event listeners
        return;
    }

    button.dataset.bound = "true"; // marks the element so I do not attach the same click event twice

    button.addEventListener("click", function () { // when the button is clicked, toggle the related panel
        this.classList.toggle("active"); // helps with styling the open state

        const panel = this.nextElementSibling; // accordion assumes the panel comes immediately after the button
        if (!panel) return; // safe guard in case the HTML structure is wrong

        panel.style.display = panel.style.display === "block" ? "none" : "block"; // simple show/hide toggle
    });
}

function initialiseStaticAccordions() { // finds all accordion buttons already written in the page and activates them
    document.querySelectorAll(".accordion").forEach(attachAccordion);
}

function initialiseChecklistCollapsible() { // similar idea, but for checklist-style collapsible buttons
    const buttons = document.querySelectorAll(".collapsible-btn"); // selects all matching collapsible buttons

    buttons.forEach(button => {
        if (button.dataset.bound === "true") return; // same duplicate-protection idea as the accordion helper
        button.dataset.bound = "true";

        button.addEventListener("click", function () {
            const content = this.nextElementSibling; // assumes the collapsible content sits right after the button
            if (!content) return;

            content.style.display = content.style.display === "block" ? "none" : "block"; // toggles visibility
        });
    });
}

     // =========================================================
    // INDEX.HTML LOGIC
    // What this section is for:
    // - keeps homepage logic in one place
    // - makes the file easier to grow later
    // =========================================================

    function initialiseIndexPage() { // this is just a starter function for the home page in case I want to add home page behaviour later
        const isIndexPage = window.location.pathname === "/" || window.location.pathname.endsWith("index.html"); // checks if the current page is the homepage
        if (!isIndexPage) return; // if I am not on the home page, this section should do nothing

        
    } 

    // =========================================================
    // CONTACT.HTML LOGIC
    // What this section is for:
    // - keeps contact page logic separate from the rest
    // - useful later if I add validation or interactive behaviour
    // =========================================================

    function initialiseContactPage() { // this is a placeholder function for contact page logic if I want to build it later
        const isContactPage = window.location.pathname.includes("contact"); // checks if the page loaded is the contact page
        if (!isContactPage) return; // if I am not on contact.html, this part should not run

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
    // CRITERIA.HTML → TICKER DROPDOWN
    // What this section is doing:
    // - fills the ticker dropdown using the full ticker universe
    // - replaces the old short hardcoded list
    // - groups tickers so the dropdown is easier to use
    // =========================================================

    function populateTickerDropdown() { // this builds the whole ticker dropdown dynamically instead of typing all options by hand in HTML
        if (!tickerSelect) return; // if the ticker dropdown is not on the page, there is nothing to build

        tickerSelect.innerHTML = ""; // clears old options first so I do not accidentally duplicate them

        const placeholder = document.createElement("option"); // creates the first default option shown before the user picks a ticker
        placeholder.value = ""; // empty value makes it easier to validate if no real ticker was chosen
        placeholder.textContent = "-- Choose a ticker --"; // text the user sees first in the dropdown
        placeholder.selected = true; // makes this the default visible option
        placeholder.disabled = false; // keeps it visible and selectable as the default top option
        tickerSelect.appendChild(placeholder); // adds the placeholder into the dropdown first

        Object.entries(tickerUniverse).forEach(([category, tickers]) => { // loops through each category and its list of tickers
            const optgroup = document.createElement("optgroup"); // creates a grouped section inside the dropdown so tickers are organised by type
            optgroup.label = category.replace(/_/g, " ").replace(/\b\w/g, char => char.toUpperCase()); // turns something like fixed_income into Fixed Income for display

            tickers.forEach(ticker => { // now loops through each ticker inside that category
                const option = document.createElement("option"); // creates one dropdown option for one ticker
                option.value = ticker; // this is the value sent when the form is submitted
                option.textContent = ticker; // this is what the user sees in the dropdown
                optgroup.appendChild(option); // puts the ticker inside the right grouped section
            });

            tickerSelect.appendChild(optgroup); // after building one full category, adds it into the select menu
        }); 
    } 

    // =========================================================
    // CRITERIA.HTML → RESETTING THE ANALYSIS AREA
    // What this section is doing:
    // - clears old analysis results
    // - prevents stale data staying on screen
    // - resets the add button and message area
    // =========================================================

    function clearAnalysisFields() { // this resets all the analysis output fields back to a neutral state
        [ // this array holds all the ids that show analysis results on the Criteria page
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
        ].forEach(id => setText(id, "N/A")); // goes through every result field and resets the visible value to N/A

        setText("result-ticker", "Select a stock to analyze"); // puts the main title back to the default message
        setText("portfolio-name", getSelectedPortfolioName()); // refreshes the portfolio name shown on screen based on the current dropdown selection

        if (addButton) { // only do this if the add button exists on this page
            addButton.disabled = true; // disables the add/update button until a new valid analysis is done
        } 

        latestAnalysis = null; // clears the saved analysis object so old data cannot be added by mistake
        clearTradeMessage(); // removes any old success or error message still showing
    } 

    // =========================================================
    // CRITERIA.HTML → CURRENT PORTFOLIO HOLDINGS DISPLAY
    // What this section is doing:
    // - builds the portfolio holdings area from backend data
    // - shows summary numbers for each portfolio
    // - creates accordion sections for cleaner viewing
    // =========================================================

    function renderPortfolioGroups(grouped) { // this takes the grouped portfolio data from Flask and turns it into visible HTML
        const container = document.getElementById("portfolio-groups"); // finds the area where the grouped portfolio sections should appear
        if (!container) return; // if that container is not on the page, nothing should be rendered

        container.innerHTML = ""; // clears old content first so I do not stack duplicated portfolio sections

        Object.entries(grouped).forEach(([, data]) => { // loops through each portfolio in the grouped data object
            const button = document.createElement("button"); // creates the accordion button for one portfolio
            button.className = "accordion portfolio-group-button"; // gives it the same style and behaviour classes as the rest of the accordions
            button.type = "button"; // makes sure it behaves like a normal button and not a submit button
            button.textContent = data.portfolio_name; // uses the portfolio name as the accordion title

            const panel = document.createElement("div"); // creates the hidden panel that opens below the button
            panel.className = "panel"; // applies the panel styling used for accordion content

            const summary = data.summary || {}; // safely reads the summary object for that portfolio, or uses an empty object if missing

            const summaryBox = document.createElement("div"); // creates a small box for the portfolio summary stats
            summaryBox.className = "portfolio-summary"; // gives it the summary styling so the layout stays neat
            summaryBox.innerHTML = `
                <p><strong>Positions:</strong> ${summary.position_count ?? 0}</p>
                <p><strong>Total Allocated:</strong> ${summary.total_allocated_percent ?? 0}%</p>
                <p><strong>Remaining Cash:</strong> ${summary.remaining_cash_percent ?? 100}%</p>
                <p><strong>Average Beta:</strong> ${summary.average_beta ?? "N/A"}</p>
            `; 
            panel.appendChild(summaryBox); // places the summary box inside the panel before the stock list

            if (!data.stocks || data.stocks.length === 0) { // checks if this portfolio currently has no saved stocks
                const empty = document.createElement("p"); // creates a simple paragraph for the empty message
                empty.textContent = "No stocks added yet."; // message shown when nothing has been added
                panel.appendChild(empty); // adds that message into the panel
            } else { // if stocks do exist, build the table instead
                const table = document.createElement("table"); // creates a table to display the saved holdings
                table.className = "table"; // uses the main table styling from the site

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

                panel.appendChild(table); // inserts the finished holdings table into the panel
            } 

            container.appendChild(button); // adds the accordion button into the portfolio groups area
            container.appendChild(panel); // adds the matching panel directly underneath the button
            attachAccordion(button); // connects accordion open/close behaviour to this new button
        }); 
    } 

    // =========================================================
    // CRITERIA.HTML → LOAD HOLDINGS FROM FLASK
    // What this section is doing:
    // - requests grouped portfolio data from the backend
    // - sends that data to the render function above
    // =========================================================

    async function loadPortfolioGroups() { // this gets the current saved portfolio holdings from Flask
        const container = document.getElementById("portfolio-groups"); // finds the place where the holdings should be shown
        if (!container) return; // if that area is not on the page, skip this request

        try { // using try/catch here so the page does not crash if the fetch fails
            const res = await fetch("/portfolio-stocks"); // asks Flask for the grouped portfolio stock data
            const data = await res.json(); // converts the JSON response into a JavaScript object
            renderPortfolioGroups(data); // sends the returned data into the render function so it appears on screen
        } catch (error) { // catches problems like failed fetch or invalid response
            console.error("Failed to load portfolio groups:", error); // prints a helpful error message in the console for debugging
        } 
    } 

    // =========================================================
    // CRITERIA.HTML → ANALYSE TICKER FORM
    // Why this section matters:
    // - sends the selected ticker and portfolio to Flask
    // - gets the analysis back without refreshing the page
    // - fills the results area with the returned data
  
    // =========================================================

    function initialiseCriteriaAnalysisForm() { // this sets up the analyse form only for the Criteria page
        if (!form) return; // if the form is not on this page, the function stops safely

        form.addEventListener("submit", async function (e) { // waits for the user to submit the form and then runs async code
            e.preventDefault(); // stops the normal page refresh because I want to handle the request with JavaScript
            clearTradeMessage(); // clears any old message before starting a fresh analysis

            const formData = new FormData(form); // collects the form values so they can be sent to Flask

            try { // using try/catch here so failed requests do not break the page
                const res = await fetch("/analyze", { // sends the form data to the Flask analyze route
                    method: "POST", // using POST because data is being submitted
                    body: formData, // sends the actual form fields
                    headers: { "X-Requested-With": "XMLHttpRequest" } // lets Flask know this is an async request from JavaScript
                });

                const data = await res.json(); // turns the server response into a JavaScript object

                if (!res.ok || data.error) { // checks if the request failed technically or if Flask returned an app-level error
                    clearAnalysisFields(); // clears old values so the page does not show stale results
                    setText("result-ticker", "Analysis Error"); // updates the heading to show that something went wrong
                    setText("decision-value", data.error || "Could not load analysis."); // shows the error inside the results area
                    showTradeMessage(data.error || "Could not load analysis.", "error"); // shows a clear message for the user
                    return; // stops here so the success logic below does not run
                } 

                latestAnalysis = data; // saves the latest successful analysis so it can be reused when adding to portfolio

                if (addButton) { // only runs if the add button exists on the page
                    addButton.disabled = false; // unlocks the button because there is now a valid analysis to save
                } 

                setText("result-ticker", `${data.ticker} — Analysis Summary`); // shows the analysed ticker in the result heading
                setText("portfolio-name", data.portfolio_name || getSelectedPortfolioName()); // shows the returned portfolio name or falls back to the dropdown value
                setText("beta-value", data.beta === null ? "N/A" : fmtNumber(data.beta)); // shows beta in a clean format
                setText("score-value", data.score ?? "N/A"); // shows the investment score
                setText("decision-value", data.decision || "N/A"); // shows the final decision label
                setText("weight-value", data.recommended_weight || "N/A"); // shows the suggested position size
                setText("sector-value", data.sector || "Unknown"); // shows sector or a fallback if missing
                setText("industry-value", data.industry || "Unknown"); // shows industry or a fallback if missing
                setText("tag-value", data.tag || "N/A"); // shows the short tag used in the UI

                if (data.one_year) { // this block fills the 1-year section if Flask returned it
                    setText("1y-er-value", fmtPercent(data.one_year.annualised_expected_return)); // expected return shown as a percentage
                    setText("1y-vol-value", fmtPercent(data.one_year.annualised_volatility)); // volatility shown as a percentage
                    setText("1y-sharpe-value", fmtNumber(data.one_year.sharpe_like)); // Sharpe-like value shown as a regular number
                    setText("1y-latest-price-value", fmtNumber(data.one_year.latest_price)); // latest price formatted nicely
                    setText("1y-price-start-value", data.one_year.price_start_date || "N/A"); // first date in the price series
                    setText("1y-price-end-value", data.one_year.price_end_date || "N/A"); // last date in the price series
                    setText("1y-price-obs-value", data.one_year.price_observations ?? "N/A"); // total number of price observations
                    setText("1y-return-start-value", data.one_year.return_start_date || "N/A"); // first return date
                    setText("1y-return-end-value", data.one_year.return_end_date || "N/A"); // last return date
                    setText("1y-return-obs-value", data.one_year.return_observations ?? "N/A"); // total number of return observations

                    if (data.one_year.forecast) { // this nested block fills the 1-year forecast section if forecast data exists
                        setText("1y-quarterly-return-value", fmtPercent(data.one_year.forecast.quarterly_return)); // quarterly return used in the forecast
                        setText("1y-q1-price-value", fmtNumber(data.one_year.forecast.q1_expected_price)); // forecasted Q1 price
                        setText("1y-q2-price-value", fmtNumber(data.one_year.forecast.q2_expected_price)); // forecasted Q2 price
                        setText("1y-q3-price-value", fmtNumber(data.one_year.forecast.q3_expected_price)); // forecasted Q3 price
                        setText("1y-q4-price-value", fmtNumber(data.one_year.forecast.q4_expected_price)); // forecasted Q4 price
                    } 
                }

                if (data.three_month) { // this block fills the 3-month section if Flask returned it
                    setText("3m-er-value", fmtPercent(data.three_month.annualised_expected_return)); // 3-month expected return
                    setText("3m-vol-value", fmtPercent(data.three_month.annualised_volatility)); // 3-month volatility
                    setText("3m-sharpe-value", fmtNumber(data.three_month.sharpe_like)); // 3-month Sharpe-like value
                    setText("3m-latest-price-value", fmtNumber(data.three_month.latest_price)); // latest price in this shorter window
                    setText("3m-price-start-value", data.three_month.price_start_date || "N/A"); // first price date in the 3-month sample
                    setText("3m-price-end-value", data.three_month.price_end_date || "N/A"); // last price date in the 3-month sample
                    setText("3m-price-obs-value", data.three_month.price_observations ?? "N/A"); // number of price rows in the 3-month sample
                    setText("3m-return-start-value", data.three_month.return_start_date || "N/A"); // first return date in the 3-month sample
                    setText("3m-return-end-value", data.three_month.return_end_date || "N/A"); // last return date in the 3-month sample
                    setText("3m-return-obs-value", data.three_month.return_observations ?? "N/A"); // number of return rows in the 3-month sample

                    if (data.three_month.forecast) { // this fills the shorter-term forecast area if forecast data is available
                        setText("3m-quarterly-return-value", fmtPercent(data.three_month.forecast.quarterly_return)); // quarterly return from the 3-month model view
                        setText("3m-q1-price-value", fmtNumber(data.three_month.forecast.q1_expected_price)); // forecasted Q1 price
                        setText("3m-q2-price-value", fmtNumber(data.three_month.forecast.q2_expected_price)); // forecasted Q2 price
                        setText("3m-q3-price-value", fmtNumber(data.three_month.forecast.q3_expected_price)); // forecasted Q3 price
                        setText("3m-q4-price-value", fmtNumber(data.three_month.forecast.q4_expected_price)); // forecasted Q4 price
                    } 
                } 

                setText("benchmark-ticker-value", data.benchmark_ticker || "N/A"); // shows which benchmark was used for beta
                setText("benchmark-start-value", data.benchmark_start_date || "N/A"); // shows benchmark data start date
                setText("benchmark-end-value", data.benchmark_end_date || "N/A"); // shows benchmark data end date
                setText("beta-obs-value", data.beta_observations ?? "N/A"); // shows how many overlapping observations were used for beta

                showTradeMessage("Analysis completed. Review mandate fit before adding to portfolio.", "info"); // gives the user a final prompt before they save the position
            } catch (error) { // catches network problems or unexpected issues
                clearAnalysisFields(); // resets the result area if something failed badly
                setText("result-ticker", "Request Failed"); // updates the heading so the failure is obvious
                setText("decision-value", "Could not load analysis."); // shows a fallback message in the decision box
                showTradeMessage("Could not load analysis.", "error"); // shows an error banner/message
                console.error(error); // logs technical detail in the browser console for debugging
            }
        }); 
    } 

    // =========================================================
    // CRITERIA.HTML → ADD / UPDATE PORTFOLIO
    // Why this section matters:
    // - saves the analysed ticker into the chosen portfolio
    // - updates an existing position if that ticker is already there
    // - refreshes the portfolio view after saving
    // =========================================================

    function initialiseCriteriaAddToPortfolio() { // this sets up the Add / Update Portfolio button logic
        if (!addButton) return; // if the button is not on the page, nothing should run

        addButton.addEventListener("click", async function () { // waits for the button click and then sends data to Flask
            if (!latestAnalysis) return; // blocks the action if there is no analysis saved yet

            const selectedPortfolioKey = portfolioSelect ? portfolioSelect.value : latestAnalysis.portfolio_key; // gets the selected portfolio key, or falls back to the last analysis
            const selectedPortfolioName = getSelectedPortfolioName(); // gets the visible portfolio name from the dropdown

            try { // wrapped in try/catch so save errors do not crash the page
                const res = await fetch("/add-to-portfolio", { // sends the stock data to Flask for validation and storage
                    method: "POST", // POST is used because we are sending new data to the backend
                    headers: { "Content-Type": "application/json" }, // tells Flask that the request body is JSON
                    body: JSON.stringify({ // turns the JavaScript object into JSON before sending it
                        ticker: latestAnalysis.ticker, // analysed ticker symbol
                        portfolio_key: selectedPortfolioKey, // selected portfolio key
                        portfolio_name: selectedPortfolioName, // selected portfolio display name
                        recommended_weight: latestAnalysis.recommended_weight, // suggested position size
                        decision: latestAnalysis.decision, // model decision
                        tag: latestAnalysis.tag, // short category tag
                        sector: latestAnalysis.sector, // sector value from analysis
                        industry: latestAnalysis.industry, // industry value from analysis
                        beta: latestAnalysis.beta // beta value from analysis
                    }) 
                }); 

                const data = await res.json(); // reads Flask response as JSON

                if (!res.ok || data.error) { // checks if Flask returned a validation problem or server-side error
                    const errors = Array.isArray(data.error) ? data.error : [data.error || "Failed to add stock."]; // makes sure errors are always handled as an array
                    const warnings = Array.isArray(data.warnings) ? data.warnings : []; // does the same for warnings
                    showTradeMessage([...errors, ...warnings], "error"); // shows all returned messages together in the UI
                    return; // stops so success logic does not run by mistake
                } 

                renderPortfolioGroups(data.portfolio); // redraws the grouped portfolio area using the updated backend data

                const messages = [data.message || "Portfolio updated."]; // starts the success message list with Flask response text
                if (Array.isArray(data.warnings) && data.warnings.length > 0) { // checks if warnings came back with a valid save
                    messages.push(...data.warnings); // adds warnings under the main success message
                } 

                showTradeMessage(messages, "success"); // shows the final success message on the page
            } catch (error) { // catches request failures or JSON parsing problems
                showTradeMessage("Failed to add to portfolio.", "error"); // shows a clean error message to the user
                console.error("Failed to add to portfolio:", error); // keeps the technical error in the console for debugging
            }
        }); 
    } 

    function initialiseCriteriaPage() { // this is the main starter function for everything related to criteria.html
        const isCriteriaPage = window.location.pathname.includes("criteria"); // checks whether the current page is really the Criteria page
        if (!isCriteriaPage) return; // if not, the whole section stops

        populateTickerDropdown(); // fills the ticker dropdown with the full ticker list
        initialiseCriteriaAnalysisForm(); // activates the analyse form logic
        initialiseCriteriaAddToPortfolio(); // activates the add/update portfolio logic
        loadPortfolioGroups(); // loads current saved holdings into the page

        if (portfolioSelect) { // only adds this listener if the dropdown exists
            portfolioSelect.addEventListener("change", function () { // runs when the user changes the portfolio
                clearAnalysisFields(); // clears old analysis because it may no longer match the new portfolio
                setText("portfolio-name", getSelectedPortfolioName()); // updates the shown portfolio name immediately
            }); 
        } 
    } 

    // =========================================================
    // MARKET_DASHBOARD.HTML → FILTERS, PRESETS, AND SORTING
    // Why this section matters:
    // - lets the user screen the investment universe quickly
    // - supports both manual filters and one-click preset buttons
    // - also allows sorting by clicking the table headers
    // =========================================================

    function initialiseMarketDashboard() { // this is the main setup function for the dashboard page
        if (!marketTable) return; // if the market table is not on this page, the dashboard logic should not run

        const tbody = marketTable.querySelector("tbody"); // gets the table body because this is where the data rows live
        const headers = marketTable.querySelectorAll("th[data-sort]"); // gets only the sortable headers

        const tickerFilter = document.getElementById("ticker-filter"); // dropdown used to filter by ticker
        const decisionFilter = document.getElementById("decision-filter"); // dropdown used to filter by decision
        const scoreFilter = document.getElementById("score-filter"); // dropdown used to filter by minimum score
        const volatilityFilter = document.getElementById("volatility-filter"); // input used to set a volatility ceiling
        const sharpeFilter = document.getElementById("sharpe-filter"); // input used to set a minimum Sharpe value
        const summary = document.getElementById("dashboard-summary"); // text area that tells the user how many rows are showing

        const presetLowRisk = document.getElementById("preset-low-risk"); // button for low-risk screen
        const presetHighConviction = document.getElementById("preset-high-conviction"); // button for high-conviction screen
        const presetCore = document.getElementById("preset-core"); // button for core holding screen
        const presetSatellite = document.getElementById("preset-satellite"); // button for satellite screen
        const presetExploratory = document.getElementById("preset-exploratory"); // button for exploratory screen
        const presetIncome = document.getElementById("preset-income"); // button for income / defensive screen
        const presetBestRanked = document.getElementById("preset-best-ranked"); // button for best-ranked screen
        const presetCash = document.getElementById("preset-cash"); // button for cash screen
        const clearFiltersBtn = document.getElementById("clear-filters"); // button that resets everything

        let activePreset = ""; // keeps track of which preset is currently active

        function applyDashboardFilters() { // this function reads the filters and decides which rows stay visible
            const rows = tbody.querySelectorAll("tr"); // gets all current rows in the market table

            const tickerValue = tickerFilter ? tickerFilter.value.toUpperCase() : ""; // reads selected ticker and standardises it to uppercase
            const decisionValue = decisionFilter ? decisionFilter.value : ""; // reads selected decision value
            const scoreValue = scoreFilter ? parseNumber(scoreFilter.value) : null; // reads score filter and safely converts it to a number
            const volatilityValue = volatilityFilter ? parseNumber(volatilityFilter.value) : null; // reads max volatility filter
            const sharpeValue = sharpeFilter ? parseNumber(sharpeFilter.value) : null; // reads min Sharpe filter

            let visibleCount = 0; // this will count how many rows survive the filters

            rows.forEach(row => { // checks every row one by one
                const rowTicker = (row.dataset.ticker || "").toUpperCase(); // gets row ticker from the data attribute
                const rowDecision = row.dataset.decision || ""; // gets row decision from the data attribute
                const rowScore = parseNumber(row.dataset.score); // gets row score
                const rowVolatility = parseNumber(row.dataset.volatility); // gets row volatility
                const rowSharpe = parseNumber(row.dataset.sharpe); // gets row Sharpe-like value

                const rowIsLowRisk = row.dataset.lowRisk === "true"; // converts low-risk flag into a true/false value
                const rowIsHighConviction = row.dataset.highConviction === "true"; // converts high-conviction flag into a true/false value
                const rowIsCoreHolding = row.dataset.coreHolding === "true"; // converts core-holding flag into a true/false value
                const rowIsSatellite = row.dataset.satellite === "true"; // converts satellite flag into a true/false value
                const rowIsExploratory = row.dataset.exploratory === "true"; // converts exploratory flag into a true/false value
                const rowIsCashCandidate = row.dataset.cashCandidate === "true"; // converts cash-candidate flag into a true/false value
                const rowIsIncomeCandidate = row.dataset.incomeCandidate === "true"; // converts income-candidate flag into a true/false value
                const rowIsBestRanked = row.dataset.bestRanked === "true"; // converts best-ranked flag into a true/false value

                let visible = true; // starts by assuming the row should be shown

                if (tickerValue && rowTicker !== tickerValue) visible = false; // hides the row if ticker does not match
                if (decisionValue && rowDecision !== decisionValue) visible = false; // hides the row if decision does not match
                if (scoreValue !== null && (rowScore === null || rowScore < scoreValue)) visible = false; // hides rows below the chosen score
                if (volatilityValue !== null && (rowVolatility === null || rowVolatility > volatilityValue)) visible = false; // hides rows above the max volatility
                if (sharpeValue !== null && (rowSharpe === null || rowSharpe < sharpeValue)) visible = false; // hides rows below the minimum Sharpe

                if (activePreset === "low-risk" && !rowIsLowRisk) visible = false; // keeps only low-risk rows when that preset is active
                if (activePreset === "high-conviction" && !rowIsHighConviction) visible = false; // keeps only high-conviction rows
                if (activePreset === "core" && !rowIsCoreHolding) visible = false; // keeps only core holdings
                if (activePreset === "satellite" && !rowIsSatellite) visible = false; // keeps only satellite rows
                if (activePreset === "exploratory" && !rowIsExploratory) visible = false; // keeps only exploratory rows
                if (activePreset === "cash" && !rowIsCashCandidate) visible = false; // keeps only cash-decision rows
                if (activePreset === "income" && !rowIsIncomeCandidate) visible = false; // keeps only income / defensive rows
                if (activePreset === "best-ranked" && !rowIsBestRanked) visible = false; // keeps only best-ranked rows

                row.style.display = visible ? "" : "none"; // either shows or hides the row in the table

                if (visible) visibleCount += 1; // adds to the count if the row is still visible
            });

            if (summary) { // only updates the summary text if that paragraph exists
                let summaryText = `Showing ${visibleCount} securities after applying filters.`; // default message after filtering

                if (activePreset === "low-risk") summaryText = `Showing ${visibleCount} low-risk securities. Filter logic: lower-volatility names that passed the model.`; // custom message for low-risk preset
                else if (activePreset === "high-conviction") summaryText = `Showing ${visibleCount} high-conviction securities. Filter logic: names classified as YES — high conviction with score 7 or above.`; // custom message for high-conviction preset
                else if (activePreset === "core") summaryText = `Showing ${visibleCount} core holdings. Filter logic: names classified as YES — core holding.`; // custom message for core preset
                else if (activePreset === "satellite") summaryText = `Showing ${visibleCount} satellite / diversifier positions. Filter logic: names classified as YES — satellite.`; // custom message for satellite preset
                else if (activePreset === "exploratory") summaryText = `Showing ${visibleCount} exploratory / high-risk positions. Filter logic: names classified as LIMITED — high risk / exploratory.`; // custom message for exploratory preset
                else if (activePreset === "income") summaryText = `Showing ${visibleCount} income / defensive securities. Filter logic: defensive or bond-style instruments flagged by the model.`; // custom message for income preset
                else if (activePreset === "best-ranked") summaryText = `Showing ${visibleCount} best-ranked securities. Filter logic: score 5 or above and Sharpe-like ratio of at least 0.3.`; // custom message for best-ranked preset
                else if (activePreset === "cash") summaryText = `Showing ${visibleCount} cash / risk-control names. Filter logic: names classified as NO — hold as cash instead.`; // custom message for cash preset

                summary.textContent = summaryText; // writes the final summary into the page
            }
        }

        function clearDashboardFilters() { // resets all filters back to their default blank state
            if (tickerFilter) tickerFilter.value = "";
            if (decisionFilter) decisionFilter.value = "";
            if (scoreFilter) scoreFilter.value = "";
            if (volatilityFilter) volatilityFilter.value = "";
            if (sharpeFilter) sharpeFilter.value = "";

            activePreset = ""; // also clears whichever preset was active
            applyDashboardFilters(); // re-runs filtering so the table refreshes immediately
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

        function getCellValue(row, index) { // small helper to read the text from one table cell
            return row.children[index].textContent.trim(); // returns the cleaned text value from that column
        }

        headers.forEach((header, index) => { // goes through every sortable table header
            header.style.cursor = "pointer"; // changes the cursor so users can see the header is clickable
            header.dataset.direction = "desc"; // stores a default starting sort direction

            header.addEventListener("click", function () { // runs when a header is clicked
                const rows = Array.from(tbody.querySelectorAll("tr")); // turns table rows into an array so JavaScript can sort them
                const direction = this.dataset.direction === "asc" ? "desc" : "asc"; // flips between ascending and descending order
                this.dataset.direction = direction; // saves the new direction on the clicked header

                rows.sort((a, b) => { // sorts the row array
                    const aText = getCellValue(a, index); // text from row a in the clicked column
                    const bText = getCellValue(b, index); // text from row b in the clicked column

                    const aNum = parseFloat(aText.replace(/[^\d.-]/g, "")); // tries to strip symbols and read the value as a number
                    const bNum = parseFloat(bText.replace(/[^\d.-]/g, "")); // same idea for row b

                    let comparison; // this will hold the comparison result
                    if (!isNaN(aNum) && !isNaN(bNum)) comparison = aNum - bNum; // uses numeric sorting if both values are numbers
                    else comparison = aText.localeCompare(bText); // otherwise falls back to text sorting

                    return direction === "asc" ? comparison : -comparison; // returns the sort result in the chosen direction
                });

                rows.forEach(row => tbody.appendChild(row)); // puts the sorted rows back into the table
                applyDashboardFilters(); // runs filters again so sorting and filtering stay in sync
            });
        });

        applyDashboardFilters(); // runs once when the page first loads so everything starts in a clean state
    }

    // =========================================================
    // PAGE STARTUP / WHAT RUNS ON LOAD
    // Why this section matters:
    // - turns on shared UI behaviour
    // - then starts the logic for whichever HTML page is currently open
    // =========================================================
    initialiseStaticAccordions(); // activates accordion buttons already on the page
    initialiseChecklistCollapsible(); // activates collapsible checklist sections
    initialiseIndexPage(); // runs homepage logic if the user is on index.html
    initialisePortfolioProfilesPage(); // runs portfolio profiles logic if that page is open
    initialiseCriteriaPage(); // runs all Criteria page logic
    initialiseMarketDashboard(); // runs all Market Dashboard logic
    initialiseContactPage(); // runs contact page logic if needed

}); 