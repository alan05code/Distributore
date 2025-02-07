<?php
    session_start();
    ob_start();

    // Verifica se l'utente è autenticato
    if (!isset($_SESSION['CodiceChiavetta'])) {
        header("Location: login/login.html"); // Reindirizza alla pagina di login se non autenticato
        exit();
    }

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
        <title>Client</title>
        <!-- CSS -->
        <link rel="stylesheet" href="../src/style.css">
        <link rel="stylesheet" href="../src/menu/offCanvas/offCanvas.css">
        <link rel="stylesheet" href="../src/menu/profile/profileMenu.css">
        <link rel="stylesheet" href="../src/warnings/warnings.css">
        <link rel="stylesheet" href="../dashboard/slot.css">
        <!-- JS -->
        <script type="text/JavaScript" src="../dashboard/slot-table.js"></script>
        <script type="text/JavaScript" src="../src/warnings/warnings.js"></script>
    </head>
    <body>
        <?php
            // Imposta il valore predefinito se non è stato selezionato nulla
            if (isset($_GET['dashboardSection'])) {
                $selectedSection = $_GET['dashboardSection'];
            } else {
                $selectedSection = isset($_SESSION['selectedSection']) ? $_SESSION['selectedSection'] : 'dashboard';
            }

            // Controlla se c'è una porzione di URL dopo l'ancora
            if(isset($_SERVER['REQUEST_URI'])) {
                $urlParts = explode('#', $_SERVER['REQUEST_URI']);
                if(count($urlParts) > 1) {
                    $sectionFromUrl = $urlParts[1];
                    
                    // Usa questa variabile per determinare quale sezione visualizzare
                    $selectedSection = $sectionFromUrl;
                }
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
                        <li><img src="../src/menu/offCanvas/img/client/history.png"><button type="submit" name="dashboardSection" value="cronologiaTransazioni">Cronologia Transazioni</button></li>
                        <li><img src="../src/menu/offCanvas/img/client/shopping-cart.png"><button type="submit" name="dashboardSection" value="acquistaProdotti">Acquista Prodotti</button></li>
                    </form>
                </ul>
            </nav>    
        </header>

        <header class='profile-menu'>
            
            <input type="checkbox" id="profile-toogle-menu" />

            <div>
                <label for="profile-toogle-menu" class="profile-toogle-open">          
                    <form id="profile-icon" method="get">
                        <input type="hidden" name="dashboardSection" value="ricaricaSaldo">
                        <input type="submit" id="profile-show-saldo" value="Saldo: <?php echo $_SESSION['Saldo']; ?>€">
                    </form>
                </label>
            </div>

            <nav>
                <div>
                    <a href=""><i class="profile- fab fa-css3-alt"></i><?php echo $_SESSION['Nome'];?></a>
                    <a href=""><i class="profile- fab fa-css3-alt"></i><?php echo $_SESSION['Cognome'];?></a>

                    <label for="profile-toogle-menu" class="profile-toogle-close">
                        <span></span>
                    </label>
                </div>
                <ul>
                    <form method="get">
                        <li><button type="submit" name="dashboardSection" value="ricaricaSaldo">Effettua Ricarica</button><img src="../src/menu/profile/img/client/wallet.png"></li>
                        <li><button type="submit" name="dashboardSection" value="modificaPIN">Modifica PIN</button><img src="../src/menu/profile/img/client/lock.png"></li>
                        <li><a href="../src/accounts/logout.php">Logout</a><img src="../src/menu/profile/img/sign-out.png"></li>
                    </form>
                </ul>
            </nav>
        </header>

        <?php
            $_SESSION['selectedSection'] = $selectedSection;
        ?>
        
        <br><br>
        <h1>Benvenuto <?php echo $_SESSION['Nome']; ?>!</h1>
        <br><br>
        
        <?php
            // Mostra la dashboard in base alla selezione dell'utente
            echo dashboard($selectedSection);
        ?>
    </body>
</html>

<?php
    // Funzione getDashboard
    function dashboard($section) {
        switch ($section) {
            case 'dashboard':
                $output = '<div id="distributoreTableContainer"></div>';
                break;
            case 'ricaricaSaldo':
                $output = aggiornaSaldo();
                break;
            case 'acquistaProdotti':
                $output = ProdottiDisponibili();
                break;
            case 'cronologiaTransazioni':
                $tipoTransazione = isset($_SESSION['tipoTransazione']) ? $_SESSION['tipoTransazione'] : 'Acquisto';
                $output = '<h2>Cronologia Acquisti</h2>';
                $output .= mostraMenu($tipoTransazione);
                $output .= cronologiaTransazioni($tipoTransazione);
                break;
            case 'modificaPIN':
                $output = modificaPIN();
                break;
            default:
                $output = '';
        }
    
        return $output;
    }
    
    // Funzione per visualizzare il menu
    function mostraMenu($tipoTransazione) {
        $opzioni = ['Ricarica', 'Acquisto']; // Opzioni disponibili
    
        $menu = '<form method="post" action="">
                    <label for="tipoTransazione">Tipo Transazione:</label>
                    <select name="tipoTransazione" id="tipoTransazione">
        ';
    
        foreach ($opzioni as $opzione) {
            $selezionato = ($opzione === $tipoTransazione) ? 'selected' : ''; // Verifica se l'opzione corrente è uguale al tipo di transazione attuale
            $menu .= '<option value="' . $opzione . '" ' . $selezionato . '>' . $opzione . '</option>';
        }
    
        $menu .= '</select>
                    <input type="submit" name="cambiaTipoTransazione" value="Cambia">
                </form>';
    
        return $menu;
    }
    
    // Gestione del cambio del tipo di transazione quando il form viene inviato
    if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['cambiaTipoTransazione'])) {
        $_SESSION['tipoTransazione'] = $_POST['tipoTransazione'];
        header('Location: ' . $_SERVER['PHP_SELF']);
        exit;
    }
?>

<?php
    // Funzione per visualizzare la ricarica del saldo
    function aggiornaSaldo(){
        $output = '<h2>Ricarica Saldo</h2>';
        $output .= '<form method="post" action="functions/functions.php">  
                <label for="importoRicarica">Importo (€):</label>
                <input type="number" name="importoRicarica" required>
                <input type="submit" name="ricarica" value="Ricarica">
            </form>';
        return $output;
    }

    // Funzione per ottenere la cronologia delle transazioni dell'utente
    function cronologiaTransazioni($tipoTransazione) {
        global $conn;

        $codiceChiavetta = $_SESSION['CodiceChiavetta'];
        
        $output = "";
        
        if ($tipoTransazione == 'Acquisto') {
            // Query per ottenere la cronologia degli acquisti
            $query = "SELECT t.IDTransazione, t.Importo, t.Quantita, p.NomeProdotto
            FROM Transazioni t
            JOIN dettaglitransazione dt ON t.IDTransazione = dt.IDTransazione
            JOIN Prodotti p ON dt.NomeProdotto = p.NomeProdotto
            ORDER BY t.IDTransazione DESC";
        
            $result = $conn->query($query);

            if ($result->num_rows > 0) {
                $output .= '<table border="1" align="center">
                            <tr>
                                <th>ID Transazione</th>
                                <th>Nome Prodotto</th>
                                <th>Quantità</th>
                                <th>Importo (€)</th>
                            </tr>';

                foreach ($result as $acquisto) {
                    $output .= '<tr>
                                    <td>' . $acquisto['IDTransazione'] . '</td>
                                    <td>' . $acquisto['NomeProdotto'] . '</td>
                                    <td>' . $acquisto['Quantita'] . '</td>
                                    <td>' . $acquisto['Importo'] . '</td>
                                </tr>';
                }

                $output .= '</table>';
            } else {
                $output .= '<h3>Nessun Acquisto Effettuato</h3>';
            }
        } else if ($tipoTransazione == 'Ricarica') {
            $query = "SELECT IDTransazione, Importo FROM Transazioni 
            WHERE CodiceChiavetta = '$codiceChiavetta' AND TipoTransazione = '$tipoTransazione'
            ORDER BY IDTransazione DESC";

            $result = $conn->query($query);

            if ($result->num_rows > 0) {
            $output .= '<table border="1" align="center">
                        <tr>
                            <th>IDTransazione</th>
                            <th>Importo</th>
                        </tr>';

            while ($row = $result->fetch_assoc()) {
            $output .= '<tr>
                            <td>' . $row['IDTransazione'] . '</td>
                            <td>' . $row['Importo'] . '</td>
                        </tr>';
            }

            $output .= '</table>';
            } else {
            $output .= '<p>Nessuna transazione trovata per il codice chiavetta ' . $codiceChiavetta . ' e il tipo di transazione ' . $tipoTransazione . '</p>';
            }
        } else {
            $output = 'Tipo transazione non valido';
        }

        // Aggiungi un pulsante "Aggiorna" che ricarica la pagina
        $output .= '<form method="post">
                        <button type="submit" name="refresh">Aggiorna</button>
                    </form>';


        return $output; // Restituisce la stringa contenente l'output
    }

    // Funzione per ottenere la lista dei prodotti disponibili
    function ProdottiDisponibili() {
        $output = '<h2>Acquista Prodotti</h2>';

        $output = '<div id="distributoreTablePurchasing"></div>';

        return $output;
    }

    // Funzione per modificare il PIN
    function modificaPIN() {
        $output = '<h2>Modifica PIN Utente</h2>';
        $output .= '<form action="functions/functions.php" method="post">
                        <label for="vecchioPIN">Vecchio PIN:</label>
                        <input type="password" id="vecchioPIN" name="vecchioPIN" required>
                        <br>

                        <label for="nuovoPIN">Nuovo PIN:</label>
                        <input type="password" id="nuovoPIN" name="nuovoPIN" required>
                        <br><br>
                        
                        <input type="submit" name="aggiornaPIN" value="aggiornaPIN">
                    </form>';
        return $output;
    }
?>