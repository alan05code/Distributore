<?php
    session_start();
    ob_start();

    try {
        // Connessione al database
        $servername = "localhost";
        $username = "root";
        $password = "";
        $dbname = "Distributore";
    
        $conn = new mysqli($servername, $username, $password, $dbname);
    
        // Controlla la connessione al database
        if ($conn->connect_error) {
            throw new Exception();
        }
    } catch (Exception) {
        header("Location: ../src/index.html?error=Connessione al database fallita");
        exit();
    }
?>

<!DOCTYPE html>
<html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Page</title>
        <!-- CSS -->
        <link rel="stylesheet" href="../src/style.css">
        <link rel="stylesheet" href="../src/menu/offCanvas/offCanvas.css">
        <link rel="stylesheet" href="../src/menu/profile/profileMenu.css">
        <link rel="stylesheet" href="../src/warnings/warnings.css">
        <link rel="stylesheet" href="../dashboard/slot.css">
        <!-- JS -->
        <script type="text/JavaScript" src="../dashboard/slot-table.js"></script>
        <script type="text/JavaScript" src="../src/warnings/warnings.js"></script>
        <script type="text/JavaScript" src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    </head>
    <body>
        <?php
            // Imposta il valore predefinito se non è stato selezionato nulla
            if (isset($_GET['dashboardSection'])) {
                $selectedSection = $_GET['dashboardSection'];
            } else {
                $selectedSection = isset($_SESSION['selectedSection']) ? $_SESSION['selectedSection'] : 'dashboard';
            }
        ?>
        <header class="offcanvas-menu">
            
            <input type="checkbox" id="toogle-menu" />
            
            <div>
                <label for="toogle-menu" class="toogle-open"><span></span></label>
                <form method="get">
                    <input type="hidden" name="dashboardSection" value="dashboard">
                    <input type="submit" value="NinjaSpenser"><i class="fab fa-css3-alt"></i>
                </form>
            </div>

            <nav>
                <div>
                    <label for="toogle-menu" class="toogle-close">
                        <span></span>
                    </label>
                </div>
                <ul>
                    <form method="get">
                        <li><img src="../src/menu/offCanvas/img/admin/folder-management.png" alt=""><button type="submit" name="dashboardSection" value="gestioneDistributore">Gestione Distributore</button></li>
                        <li><img src="../src/menu/offCanvas/img/admin/data-management.png" alt=""><button type="submit" name="dashboardSection" value="gestioneProdotti">Gestione Prodotti</button></li>
                        <li><img src="../src/menu/offCanvas/img/admin/history.png" alt=""><button type="submit" name="dashboardSection" value="cronologiaTransazioni">Cronologia Transazioni</button></li>
                        <li><img src="../src/menu/offCanvas/img/admin/trend.png" alt=""><button type="submit" name="dashboardSection" value="venditeProdotti">Prodotti Venduti</button></li>
                        <li><img src="../src/menu/offCanvas/img/admin/user.png" alt=""><button type="submit" name="dashboardSection" value="acquistiPerChiavetta">Acquisti per Chiavetta</button></li>
                    </form>
                </ul>
            </nav>    
        </header>

        <header class='profile-menu'>
            
            <input type="checkbox" id="profile-toogle-menu" />

            <div>
                <!-- apri menu profile -->
                <label for="profile-toogle-menu" class="profile-toogle-open"></label>
                <form method="get">
                    <input type="hidden">
                    <input type="submit" value="ADMIN">
                </form>
            </div>

            <nav>
                <div>
                    <label for="profile-toogle-menu" class="profile-toogle-close">
                        <span></span>
                    </label>
                </div>
                <ul>
                    <form method="get">
                        <li><button type="submit" name="dashboardSection" value="guadagnoTotale">Guadagno Totale</button><img src="../src/menu/profile/img/admin/piggy-bank.png" alt=""></li>
                        <li><a href="../src/accounts/logout.php">Logout</a><img src="../src/menu/profile/img/sign-out.png" alt=""></li>
                    </form>
                </ul>
            </nav>
        </header>

        <?php
            // Conserva la selezione nella sessione
            $_SESSION['selectedSection'] = $selectedSection;
        ?>
        
        <br><br>
        <h1>Admin Page</h1>
        
        <?php
            // Mostra la dashboard in base alla selezione dell'utente
            echo dashboard($selectedSection);
        ?>

        <br>
    </body>
</html>

<?php
    // Funzione dashboard
    function dashboard($section) {
        switch ($section) {
            case 'dashboard':
                $output = '<div id="distributoreTableContainer"></div>';
                break;
            case 'guadagnoTotale':
                $output = guadagnoTotale();
                break;
            case 'gestioneDistributore':
                $output = gestioneDistributore();
                break;   
            case 'gestioneProdotti':
                $output = gestioneProdotti();
                break;
            case 'cronologiaTransazioni':
                $output = cronologiaTransazioni();
                break;
            case 'venditeProdotti':
                $output = venditeProdotti();
                break;
            case 'acquistiPerChiavetta':
                $output = acquistiPerChiavetta();
                break;
            default:
                $output = "";
        }

        return $output;
    }
?>

<?php
    // Funzioni di supporto
    ////////////////////////
    // Seleziona un dato da una tabella di un database
    function distinctValues($columnName, $tableName) {
        global $conn;
        $sql = "SELECT DISTINCT $columnName FROM $tableName";
        $result = $conn->query($sql);
        return $result->fetch_all(MYSQLI_ASSOC);
    }
    // Genera un barra di ricerca
    function printSearchForm($searchTerm) {
        return '<form method="get" action="">
                    <label for="search">🔍Ricerca:</label>
                    <input type="text" name="search" id="search" value="' . $searchTerm . '" placeholder="Parola Chiave">
                    <br>
                    <label for="order">Ordina per:</label>
                    <select name="order" id="order">
                        <option value="NomeProdotto" ' . ($_SESSION['order'] == 'NomeProdotto' ? 'selected' : '') . '>Nome Prodotto</option>
                        <option value="QuantitaDisponibile" ' . ($_SESSION['order'] == 'QuantitaDisponibile' ? 'selected' : '') . '>Quantità Disponibile</option>
                        <option value="Prezzo" ' . ($_SESSION['order'] == 'Prezzo' ? 'selected' : '') . '>Prezzo</option>
                    </select>
                    <label for="orderDirection">Ordinamento:</label>
                    <select name="orderDirection" id="orderDirection">
                        <option value="ASC" ' . ($_SESSION['orderDirection'] == 'ASC' ? 'selected' : '') . '>Crescente</option>
                        <option value="DESC" ' . ($_SESSION['orderDirection'] == 'DESC' ? 'selected' : '') . '>Decrescente</option>
                    </select>
                    <br>
                    <input type="submit" value="Cerca">
                </form>';
    }
    //////////////////////////////////////////////   

    
    // Funzione gestioneProdotti
    function gestioneProdotti() {
        echo "<br><br><h2>Gestione Prodotti</h2>";
    
        global $conn;
        
        // Ottenimento della query di DEFAULT
        $sqlProducts = "SELECT Immagine 
                        FROM Prodotti 
                        WHERE NomeProdotto = 'Vuoto'";
        $result = $conn->query($sqlProducts);
        
        // Verifica se la query ha prodotto dei risultati
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $newProductImage = $row['Immagine'];
        } else {
            $newProductImage = "";
        }  

        // Gestione dell'ordinamento
        $order = isset($_GET['order']) ? $_GET['order'] : 'nomeProdotto';
        $_SESSION['order'] = $order;
    
        // Gestione della direzione dell'ordinamento
        $orderDirection = isset($_GET['orderDirection']) ? $_GET['orderDirection'] : 'ASC';
        $_SESSION['orderDirection'] = $orderDirection;
    
        // Gestione della ricerca
        $searchTerm = isset($_GET['search']) ? $_GET['search'] : '';
    
        // Costruzione della query SQL
        $sqlProducts = "SELECT NomeProdotto, QuantitaDisponibile, Prezzo, Immagine FROM Prodotti 
                        WHERE (NomeProdotto LIKE '%$searchTerm%'
                        OR QuantitaDisponibile LIKE '%$searchTerm%'
                        OR Prezzo LIKE '%$searchTerm%')
                        AND NomeProdotto <> 'Vuoto'
                        ORDER BY {$_SESSION['order']} {$_SESSION['orderDirection']}";
    
        // Esecuzione della query
        $resultProducts = $conn->query($sqlProducts);
        $products = $resultProducts->fetch_all(MYSQLI_ASSOC);
    
        // Stili CSS
        echo '<style>
                th a {
                    color: black;
                    text-decoration: none;
                }
              </style>';
    
        // Creazione della tabella HTML
        $tableHTML = printSearchForm($searchTerm);
        $tableHTML .= '<table border="1" align="center">
        <tr>
            <th><a href="?order=NomeProdotto">Nome Prodotto</a></th>
            <th><a href="?order=QuantitaDisponibile">Quantità Disponibile</a></th>
            <th><a href="?order=Prezzo">Prezzo</a></th>
            <th>Immagine</th>
            <th>Azioni</th>
        </tr>';

        // Stampa delle righe della tabella
        foreach ($products as $index => $prodotto) {
            $tableHTML .= '<tr>
                            <form method="post" action="interfaceDB/updateProductDB.php" enctype="multipart/form-data">
                                <td>' . $prodotto['NomeProdotto'] . '</td>
                                <td>
                                    <input type="hidden" name="nomeProdotto" value="' . $prodotto['NomeProdotto'] . '">
                                    <input type="text" name="nuovaQuantita" value="' . $prodotto['QuantitaDisponibile'] . '">
                                </td>
                                <td>
                                    <input type="hidden" name="nomeProdotto" value="' . $prodotto['NomeProdotto'] . '">
                                    <input type="text" name="nuovoPrezzo" value="' . $prodotto['Prezzo'] . '">
                                </td>
                                <td>
                                    <div class="change-product-image">
                                        <label for="file-upload-' . $index . '">
                                            <img id="current-image-' . $index . '" src="' . $prodotto['Immagine'] . '" alt="Immagine Prodotto">
                                        </label>
                                        <input type="file" id="file-upload-' . $index . '" name="immagineProdotto" placeholder="' . $prodotto['Immagine'] . '" onchange="previewFile(this, ' . $index . ', \'' . $prodotto['Immagine'] . '\')">
                                    </div>
                                </td>
                                <td>
                                    <input type="submit" value="Salva">
                                    <a href="interfaceDB/deleteProductDB.php?nomeProdotto=' . $prodotto['NomeProdotto'] . '">
                                        <button type="button">Rimuovi</button>
                                    </a>
                                </td>
                            </form>
                        </tr>';  
        }

        // Aggiunta di una riga per inserire un nuovo prodotto
        $tableHTML .= '<tr>
                            <form method="post" action="interfaceDB/insertProductDB.php" enctype="multipart/form-data">
                                <td><input type="text" name="nuovoNomeProdotto" placeholder="Nome Prodotto" required></td>
                                <td><input type="text" name="nuovaQuantita" placeholder="Quantità" required></td>
                                <td><input type="text" name="nuovoPrezzo" placeholder="Prezzo" required></td>
                                <td>
                                    <div class="change-product-image">
                                        <label for="file-upload-nuovo">
                                            <img id="current-image-nuovo" src="' . $newProductImage . '" alt="Immagine Prodotto">
                                        </label>
                                        <input type="file" id="file-upload-nuovo" name="immagineProdotto" onchange="previewFile(this, \'nuovo\', \'' . $newProductImage . '\')">
                                    </div>
                                </td>
                                <td><input type="submit" value="Aggiungi"></td>
                            </form>
                        </tr>';
    
        $tableHTML .= '</table>';
        
        ?>
        <script>
            // Funzione per mostrare l'anteprima del file
            function previewFile(input, index, oldImg) {
                var preview = document.getElementById('current-image-' + index);
                var file = input.files[0];
                var reader = new FileReader();

                reader.onloadend = function() {
                    preview.src = reader.result;
                }

                if (file) {
                    reader.readAsDataURL(file);
                } else {
                    preview.src = oldImg; // Ripristina l'immagine attuale se non viene selezionato alcun file
                }
            }
        </script>
        <?php
        
        return $tableHTML;
    }
    

    // Funzione gestioneDistributore
    function gestioneDistributore() {
        echo "<br><br><h2>Gestione Distributore</h2>";
    
        global $conn;

        $output = '<br><form action="interfaceDB/updateSlotDB.php" method="post">
                        <table>
                            <tr>
                                <th colspan=3>Distributore</th>
                            </tr>';

        // Query per recuperare i nomi dei prodotti dalla tabella Prodotti
        $product_name_query = "SELECT NomeProdotto, Prezzo FROM Prodotti 
                                ORDER BY NomeProdotto ASC";

        $result_Product_name = $conn->query($product_name_query);
        $product_name = $result_Product_name->fetch_all(MYSQLI_ASSOC);


        // Query per recuperare i dati dalla tabella ContenutoDistributore
        $sql = "SELECT Slot, NomeProdotto, Prezzo, Quantita 
                FROM ContenutoDistributore";

        $result = $conn->query($sql);
        $slot_data = $result->fetch_all(MYSQLI_ASSOC);

        $cell_counter = 0;

        if ($result->num_rows > 0) {
            foreach ($slot_data as $row) {
                if ($cell_counter % 3 == 0) {
                    $output .= "<tr>";
                }
                $output .= "<td>
                                <label>Slot: " . $row["Slot"] . "</label>
                                <strong>Nome Prodotto:</strong> 
                                <select class='product-select' data-slot='" . $row["Slot"] . "' name='product_cell_" . $row["Slot"] . "' id='product_cell_" . $row["Slot"] . "'>
                                    <option disabled>Seleziona un prodotto</option>";
                                    foreach ($product_name as $product) {
                                        $selected = ($product['NomeProdotto'] == $row['NomeProdotto']) ? 'selected' : '';
                                        $output .= '<option value="' . $product['NomeProdotto'] . '" ' . $selected . '>'
                                            . $product['NomeProdotto'] . '</option>';
                                    }
                $output .= "    </select><br>
                                <label for='price_cell_" . $row["Slot"] . "'>Prezzo:</label>
                                <input type='text' id='price_cell_" . $row["Slot"] . "' name='price_cell_" . $row["Slot"] . "' value='" . $row["Prezzo"] . "'><br>
                                <label for='quantity_cell_" . $row["Slot"] . "'>Quantità:</label>
                                <input type='text' id='quantity_cell_" . $row["Slot"] . "' name='quantity_cell_" . $row["Slot"] . "' value='" . $row["Quantita"] . "'>
                                <input type='hidden' name='slot_" . $row["Slot"] . "' value='" . $row["Slot"] . "'>
                            </td>";
                $cell_counter++;
                if ($cell_counter % 3 == 0) {
                    $output .= "</tr>";
                }
            }
            // Aggiungiamo celle vuote per completare la griglia 3x3
            while ($cell_counter % 3 != 0) {
                $output .= "<td></td>";
                $cell_counter++;
            }
        } else {
            $output .= "<tr><td colspan='3'>Nessun risultato trovato</td></tr>";
        }

        $output .= "</table>";

        $output .= '<br><button type="submit" name="update_button" id="update_button">Aggiorna</button>
                        <button type="submit" name="annulla" id="annulla">Annulla</button>
            </form>';
        ?>

        <script>
            document.addEventListener("DOMContentLoaded", function() {
                // Gestione delle modifiche del prezzo
                var priceInputs = document.querySelectorAll("[id^='price_cell_']");
                priceInputs.forEach(function(priceInput) {
                    priceInput.addEventListener("input", function() {
                        updateCellByInput(this);
                    });
                });

                // Gestione delle modifiche della quantità
                var quantityInputs = document.querySelectorAll("[id^='quantity_cell_']");
                quantityInputs.forEach(function(quantityInput) {
                    quantityInput.addEventListener("input", function() {
                        updateCellByInput(this);
                    });
                });

                // Gestione del cambiamento del prodotto
                var selects = document.querySelectorAll(".product-select");
                selects.forEach(function(select) {
                    select.addEventListener("change", function() {
                        var selectedName = this.value;
                        var priceInput = document.getElementById("price_cell_" + this.getAttribute("data-slot"));
                        var quantitaInput = document.getElementById("quantity_cell_" + this.getAttribute("data-slot"));
                        
                        updateCellByInput(this);

                        if (selectedName === "Vuoto") {
                            priceInput.value = "0";
                            quantitaInput.value = "0";
                            priceInput.disabled = true;
                            quantitaInput.disabled = true;
                        } else {
                            $.ajax({
                                url: "interfaceDB/getProductPrice.php",
                                type: "POST",
                                data: { nomeProdotto: selectedName },
                                success: function(data) {
                                    var result = JSON.parse(data);
                                    priceInput.value = result.Prezzo;
                                    quantitaInput.value = "10";
                                    priceInput.disabled = false;
                                    quantitaInput.disabled = false;
                                }
                            });
                        }
                    });
                });

                function updateCellByInput(input) {
                    var cell = input.parentElement;
                    cell.classList.add("selected");
                }
            });
        </script>
        
        <?php

        $conn->close();

        return $output;
    }


    // Funzioni di supporto x CronologiaTransazioni
    //////////////////////////////////////////////    
    function printFiltersForm($chiavette, $tipiTransazione, $filtroChiavetta, $filtroTipoTransazione, $searchTerm) {
        $tableHTML = '<form method="get" action="">
                        <label for="filtroRicerca">🔍Ricerca:</label>
                        <input type="text" name="filtroRicerca" id="filtroRicerca" value="' . $searchTerm . '" placeholder="Parola Chiave">
                        <br>
                        <label for="filtroChiavetta">Filtra per Codice Chiavetta:</label>
                        <select name="filtroChiavetta" id="filtroChiavetta">
                            <option value="">Tutti</option>';
        
        foreach ($chiavette as $chiavetta) {
            $selected = ($chiavetta['CodiceChiavetta'] == $filtroChiavetta) ? 'selected' : '';
            $tableHTML .= '<option value="' . $chiavetta['CodiceChiavetta'] . '" ' . $selected . '>' . $chiavetta['CodiceChiavetta'] . '</option>';
        }
    
        $tableHTML .= '</select>
                        <br>
                        <label for="filtroTipoTransazione">Filtra per Tipo Transazione:</label>
                        <select name="filtroTipoTransazione" id="filtroTipoTransazione">
                            <option value="">Tutti</option>';
        
        foreach ($tipiTransazione as $tipoTransazione) {
            $selected = ($tipoTransazione['TipoTransazione'] == $filtroTipoTransazione) ? 'selected' : '';
            $tableHTML .= '<option value="' . $tipoTransazione['TipoTransazione'] . '" ' . $selected . '>' . $tipoTransazione['TipoTransazione'] . '</option>';
        }
    
        $tableHTML .= '</select>
                        <br>
                        <input type="submit" value="Filtra">
                        <input type="submit" name="reset" value="Reset">
                    </form>';
    
        return $tableHTML;
    } 
    //////////////////////////////////////////////
    // Funzione per ottenere la cronologia delle transazioni
    function cronologiaTransazioni() {
        echo "<br><br><h2>Cronologia Transazioni:</h2>";
    
        global $conn;
    
        $chiavette = distinctValues("CodiceChiavetta", "Transazioni");
        $tipiTransazione = distinctValues("TipoTransazione", "Transazioni");
    
        // Valori di Default nei filtri
        $filtroChiavetta = isset($_GET['filtroChiavetta']) ? $_GET['filtroChiavetta'] : '';
        $filtroTipoTransazione = isset($_GET['filtroTipoTransazione']) ? $_GET['filtroTipoTransazione'] : '';
        $filtroRicerca = isset($_GET['filtroRicerca']) ? $_GET['filtroRicerca'] : '';
    
        // Verifica se è stato premuto il tasto "Reset"
        if (isset($_GET['reset'])) {
            // Reimposta i filtri ai valori di default
            $filtroChiavetta = '';
            $filtroTipoTransazione = '';
            $filtroRicerca = '';
        }
    
        $sql = "SELECT t.IDTransazione, t.CodiceChiavetta, t.TipoTransazione, t.Importo, t.Quantita, dt.NomeProdotto
                FROM Transazioni AS t
                LEFT JOIN Dettaglitransazione AS dt ON t.IDTransazione = dt.IDTransazione
                
                WHERE ('$filtroChiavetta' = '' OR t.CodiceChiavetta = '$filtroChiavetta')
                    AND ('$filtroTipoTransazione' = '' OR t.TipoTransazione = '$filtroTipoTransazione')
                    AND (
                        CONVERT(t.IDTransazione, CHAR) LIKE '%$filtroRicerca%'
                        OR CONVERT(t.Importo, CHAR) LIKE '%$filtroRicerca%'
                        OR t.CodiceChiavetta LIKE '%$filtroRicerca%'
                        OR dt.NomeProdotto LIKE '%$filtroRicerca%'
                    )
                ORDER BY t.IDTransazione DESC";

        
    

        $result = $conn->query($sql);
    
        // Aggiungi alla tabella la sezione filtri
        $tabella = printFiltersForm($chiavette, $tipiTransazione, $filtroChiavetta, $filtroTipoTransazione, $filtroRicerca);
        
        if ($filtroTipoTransazione == 'Acquisto') {
            $tabella .= '<table border="1" align="center">
                            <tr>
                                <th>ID Transazione</th>
                                <th>Codice Chiavetta</th>
                                <th>Nome Prodotto</th>
                                <th>Quantità</th>
                                <th>Importo</th>
                                <th>Azioni</th>
                            </tr>';
                
            if ($result->num_rows > 0) {
                // Aggiungi righe alla tabella HTML con i dati delle transazioni
                while ($transazione = $result->fetch_assoc()) {
                    $tabella .= '<tr>
                                    <td>' . $transazione['IDTransazione'] . '</td>
                                    <td>' . $transazione['CodiceChiavetta'] . '</td>
                                    <td>' . $transazione['NomeProdotto'] . '</td>
                                    <td>' . $transazione['Quantita'] . '</td>
                                    <td>' . $transazione['Importo'] . '</td>
                                    <td>
                                        <form method="post" action="interfaceDB/deleteTransazione.php">
                                            <input type="hidden" name="idTransazione" value="' . $transazione['IDTransazione'] . '">
                                            <input type="submit" value="Rimuovi">
                                        </form>
                                    </td>
                                </tr>';       
                }
            } else {
                $tabella .= '<tr>
                                <td colspan="6">Nessuna transazione disponibile.</td>
                            </tr>';
            }
        
            $tabella .= '</table>';
        } else {
            $tabella .= '<table border="1" align="center">
                            <tr>
                                <th>ID Transazione</th>
                                <th>Codice Chiavetta</th>
                                <th>Importo</th>
                                <th>Azioni</th>
                            </tr>';
                
            if ($result->num_rows > 0) {
                // Aggiungi righe alla tabella HTML con i dati delle transazioni
                while ($transazione = $result->fetch_assoc()) {
                    $tabella .= '<tr>
                                    <td>' . $transazione['IDTransazione'] . '</td>
                                    <td>' . $transazione['CodiceChiavetta'] . '</td>
                                    <td>' . $transazione['Importo'] . '</td>
                                    <td>
                                        <form method="post" action="interfaceDB/deleteTransazione.php">
                                            <input type="hidden" name="idTransazione" value="' . $transazione['IDTransazione'] . '">
                                            <input type="submit" value="Rimuovi">
                                        </form>
                                    </td>
                                </tr>';       
                }
            } else {
                $tabella .= '<tr>
                                <td colspan="4">Nessuna transazione disponibile.</td>
                            </tr>';
            }
        
            $tabella .= '</table>';
        }
    
        return $tabella;
    }


    function guadagnoTotale() {
        echo "<br><br><h2>Guadagno Totale</h2>";

        global $conn;
    
        $sqlGuadagnoTotale = "SELECT GuadagnoTotale, BestSellerID, Dates FROM Statistiche ORDER BY Dates DESC LIMIT 1";
        $resultGuadagnoTotale = $conn->query($sqlGuadagnoTotale);
        $guadagnoTotale = $resultGuadagnoTotale->fetch_assoc();
    
        // Formatta la data nel formato Y-m-d H:i:s
        $dataAggiornamento = date("d/m/Y", strtotime($guadagnoTotale['Dates']));
    
        $output =  '<br><p>Guadagno Totale: ' . $guadagnoTotale['GuadagnoTotale'] . '<br>Best Seller: ' . $guadagnoTotale['BestSellerID'] . '<br>Ultimo Aggiornamento: ' . $dataAggiornamento. '<br></p>';
        
        $output .= '<br><a id="refresh-btn" href="interfaceDB/getGuadagnoTotale.php">Aggiorna</a>';

        return $output;
    }


    function venditeProdotti() {
        echo "<br><br><h2>Prodotti venduti</h2>";

        global $conn;

        $sqlVendite = "SELECT nomeProdotto, NomeProdotto, QuantitaVenduta FROM Prodotti 
                    WHERE NomeProdotto <> 'Vuoto'
                    ORDER BY QuantitaVenduta DESC";
        
        $result = $conn->query($sqlVendite);

        if ($result->num_rows > 0) {
            // Inizializza la tabella HTML
            $tableHTML = '<table border="1" align="center">
                            <tr>
                                <th>Nome Prodotto</th>
                                <th>Quantità Venduta</th>
                            </tr>';

            // Aggiungi righe alla tabella HTML con i dati delle vendite
            while ($vendita = $result->fetch_assoc()) {
                $tableHTML .= '<tr>
                                    <td>' . $vendita['NomeProdotto'] . '</td>
                                    <td>' . $vendita['QuantitaVenduta'] . '</td>
                                </tr>';
            }
            $tableHTML .= '</table>';

            return $tableHTML;
        } else {
            // Nessuna vendita trovata
            return "<h4>Nessuna vendita disponibile<h4>";
        }
    }


    function acquistiPerChiavetta() {
        echo "<br><br><h2>Acquisti per chiavetta</h2>";

        global $conn;
        
        $sql = "SELECT CodiceChiavetta, NumeroAcquisti, TotaleAcquisti, TotaleRicariche
                FROM Utenti 
                ORDER BY CodiceChiavetta";

        $sqlacquisti = $conn->query($sql);

        $tableHTML = '<table border="1" align="center">
                        <tr>
                            <th>ID Utente</th>
                            <th>Numero Acquisti</th>
                            <th>Totale Acquistato</th>
                            <th>Totale Ricaricato</th>
                        </tr>';
        
        while ($acquisto = $sqlacquisti->fetch_assoc()) {
            $tableHTML .= '<tr>
                            <td><a id="table-shortcut" href="admin.php?dashboardSection=cronologiaTransazioni&filtroRicerca=&filtroChiavetta=' . $acquisto['CodiceChiavetta'] . '&filtroTipoTransazione=Acquisto">' . $acquisto['CodiceChiavetta'] . '</a></td>
                            <td>' . $acquisto['NumeroAcquisti'] . '</td>
                            <td>' . $acquisto['TotaleAcquisti'] . '</td>
                            <td>' . $acquisto['TotaleRicariche'] . '</td>
                        </tr>';
        }
        
        $tableHTML .= '</table>';
        
        return $tableHTML;
    }
?>