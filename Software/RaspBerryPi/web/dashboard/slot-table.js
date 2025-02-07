document.addEventListener("DOMContentLoaded", function () {
    fetchAndDisplayTable("distributoreTableContainer", displayDistributoreTable);
    fetchAndDisplayTable("distributoreTablePurchasing", displayDistributoreTablePurchasing, resetErogazione);
});

function fetchAndDisplayTable(containerId, displayFunction, erogazioneCallback) {
    fetch("../dashboard/get_data.php")
        .then(response => response.json())
        .then(data => {
            displayFunction(data, containerId);

            data.forEach(item => {
                if (item.Erogazione == true) {
                    setTimeout(() => { erogazioneCallback(item.Slot); }, 5000);
                }
            })
        })
        .catch(error => console.error('Error fetching data:', error));
}

function displayDistributoreTable(data, containerId) {
    const tableContainer = document.getElementById(containerId);
    const table = document.createElement("table");
    table.classList.add("custom-table");

    for (let i = 0; i < 3; i++) {
        const row = table.insertRow();
        for (let j = 1; j <= 3; j++) {
            const cell = row.insertCell();
            const slotData = data[i * 3 + j - 1];

            if (slotData && slotData.NomeProdotto != 'Vuoto') {
                cell.innerHTML += `<span class=product-name>${slotData.NomeProdotto}</span>`;
                cell.innerHTML += `<img class="product-image" src=${slotData.ImmagineProdotto}><br>`;

                if (slotData.Quantita == 0) {
                    cell.innerHTML += `<span class=noproduct>Esaurito</span>`;
                } else {
                    cell.innerHTML += `<span class=product-price>${slotData.Prezzo}€</span>`;
                    cell.innerHTML += `<span class=product-quantity>Q:${slotData.Quantita}</span>`;
                }
            } else {
                cell.classList.add("unavailable");
                cell.textContent += `Nessun Prodotto`;
            }

            cell.innerHTML += `<span class="product-slot">${slotData.Slot}</span>`;
        }
    }

    tableContainer.appendChild(table);
}

function displayDistributoreTablePurchasing(data, containerId) {
    const tableContainer = document.getElementById(containerId);
    const table = document.createElement("table");
    table.classList.add("custom-table");

    for (let i = 0; i < 3; i++) {
        const row = table.insertRow();
        for (let j = 1; j <= 3; j++) {
            const cell = row.insertCell();
            const slotData = data[i * 3 + j - 1];

            if (slotData && slotData.NomeProdotto != 'Vuoto') {
                cell.innerHTML += `<span class=product-name>${slotData.NomeProdotto}</span>`;
                cell.innerHTML += `<img class="product-image" src=${slotData.ImmagineProdotto}><br>`;

                // Verifica stato Erogazione
                if (slotData.Erogazione == true) {
                    cell.classList.add("erogazione");
                    cell.innerHTML += `<span class="erogazione-text">In Erogazione</span>`;
                }

                if (slotData.Quantita == 0) {
                    cell.innerHTML += `<span class=noproduct>Esaurito</span>`;
                } else {
                    cell.innerHTML += `<span class=product-purchasing>
                                            <form method="post" action="purchasing/summary.php">
                                                <input type="hidden" name="nomeProdotto" value="${slotData.NomeProdotto}">
                                                <input type="hidden" name="prezzo" value="${slotData.Prezzo}">
                                                <div class=product-quantity>
                                                    <label for="quantita">Q:</label>
                                                    <input type="number" name="quantita" value="1" min="1" max="${slotData.Quantita}" required>
                                                </div>
                                                <input type="submit" name="acquista" value="${slotData.Prezzo}€">
                                            </form>
                                        </span>`;
                }
            } else {
                cell.classList.add("unavailable");
                cell.textContent += `Nessun Prodotto`;
            }

            cell.innerHTML += `<span class="product-slot">${slotData.Slot}</span>`;
        }
    }

    tableContainer.appendChild(table);
}

function resetErogazione(slot) {
    // Parametri per la richiesta fetch
    const params = new URLSearchParams();
    params.append('slot', slot);

    // Opzioni della richiesta fetch
    const options = {
        method: 'POST',
        body: params,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    };

    // Effettua la richiesta fetch
    fetch("purchasing/reset_erogazione.php", options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Errore nella richiesta AJAX');
            }
            return response.text();
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Errore:', error);
        });

    // Rimuove le classi e il testo di erogazione
    const tableContainer = document.getElementById("distributoreTablePurchasing");
    const cells = tableContainer.querySelectorAll(".erogazione");

    cells.forEach(cell => {
        cell.classList.remove("erogazione");
        const erogazioneText = cell.querySelector(".erogazione-text");
        if (erogazioneText) {
            erogazioneText.remove();
        }
    });
}