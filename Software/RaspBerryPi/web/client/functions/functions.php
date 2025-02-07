<?php
    session_start();
    ob_start();

    // Connessione al database
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    // Controlla la connessione al database
    if ($conn->connect_error) {
        die("Connessione al database fallita: " . $conn->connect_error);
    }
?>

<?php
    // Risposta al form
    if ($_SERVER["REQUEST_METHOD"] == "POST") {

        if (isset($_POST['confermaOrdine'])) {
            $nomeProdotto = $_POST['nomeProdotto'];
            $quantita = $_POST['quantita'];
            $prezzo = $_POST['prezzo'];
            
            effettuaAcquisto($_SESSION['CodiceChiavetta'], $nomeProdotto, $quantita, $prezzo);
        }
        if (isset($_POST['annullaOrdine'])) {
            header("Location: ../client.php");
            exit();
        }
        if (isset($_POST['ricarica'])) {
            $importoRicarica = $_POST['importoRicarica'];
            modificaSaldo($_SESSION['CodiceChiavetta'], $importoRicarica);
        }
        if (isset($_POST['aggiornaPIN'])) {
            $nuovoPIN = $_POST['nuovoPIN'];
            $vecchioPIN = $_POST['vecchioPIN'];
            aggiornaPin($_SESSION['CodiceChiavetta'], $nuovoPIN, $vecchioPIN);
        }
        // Torna a client.php
        header("Location: ../client.php?error=ERRORE, qualcosa è andato storto");
        exit();
    }
?>

<?php
    // Funzione per modificare il PIN dell'utente
    function aggiornaPin($codiceChiavetta, $nuovoPIN, $vecchioPIN) {
        global $conn;

        // Query per ottenere il PIN attuale dell'utente
        $query = "SELECT PIN FROM utenti
                WHERE CodiceChiavetta = '$codiceChiavetta'";
        $result = $conn->query($query);

        // Verifica se la query è stata eseguita con successo
        if (!$result) {
            die("Errore durante l'esecuzione della query: " . $conn->error);
        }

        // Estrai il PIN dalla riga restituita dalla query
        $row = $result->fetch_assoc();
        $PIN = $row['PIN'];

        if($PIN == $vecchioPIN) {
            // Query di aggiornamento del PIN ed esecuzione
            $query = "UPDATE Utenti SET PIN = '$nuovoPIN'
                    WHERE CodiceChiavetta = '$codiceChiavetta'";
            $result = $conn->query($query);

            // Verifica se l'aggiornamento è stato eseguito con successo
            if ($result) {
                header("Location: ../../src/accounts/logout.php");
                exit();
            } else {
                header("Location: ../client.php?error=Errore durante l'aggiornamento del PIN: " . $conn->error );
                exit();
            }
        } else {
            echo "Errore durante l'aggiornamento del PIN: PIN ERRATO";
            header("Location: ../client.php?error=PIN ERRATO");
            exit();
        }
    }

     // Funzione per effettuare un acquisto
    function effettuaAcquisto($codiceChiavetta, $nomeProdotto, $quantita, $prezzo) {
        global $conn;

        // Ottieni il saldo attuale dell'utente
        $querySaldo = "SELECT Saldo FROM Utenti WHERE CodiceChiavetta = '$codiceChiavetta'";
        $resultSaldo = $conn->query($querySaldo);

        if ($resultSaldo->num_rows > 0) {
            $saldoAttuale = $resultSaldo->fetch_assoc()['Saldo'];

            // Calcola l'importo dell'acquisto
            $importoAcquisto = $quantita * $prezzo;

            // Verifica se l'utente ha abbastanza saldo
            if ($saldoAttuale >= $importoAcquisto) {
                // Inserisci la transazione
                $queryTransazione = "INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo, Quantita) 
                                    VALUES ('$codiceChiavetta', 'Acquisto', $importoAcquisto, $quantita)";
                $conn->query($queryTransazione);

                // Ottieni l'ID della transazione appena inserita
                $idTransazione = $conn->insert_id;
                // Inserisci il dettaglio della transazione
                $queryDettagli = "INSERT INTO DettagliTransazione (IDTransazione, NomeProdotto) 
                                VALUES ($idTransazione, '$nomeProdotto')";
                $conn->query($queryDettagli);

                // Aggiorna la quantità venduta e disponibile nel prodotto
                $queryAggiornaProdotti = "UPDATE Prodotti 
                                        SET QuantitaVenduta = QuantitaVenduta + $quantita, QuantitaDisponibile = QuantitaDisponibile - $quantita 
                                        WHERE NomeProdotto = '$nomeProdotto'";
                $conn->query($queryAggiornaProdotti);

                $queryAggiornaContenutoDistributore = "UPDATE ContenutoDistributore
                                        SET Quantita = Quantita - $quantita, Erogazione = TRUE
                                        WHERE NomeProdotto = '$nomeProdotto'";
                $conn->query($queryAggiornaContenutoDistributore);

                // Aggiorna il saldo dell'utente
                $queryAggiornaSaldo = "UPDATE Utenti SET Saldo = Saldo - $importoAcquisto 
                                    WHERE CodiceChiavetta = '$codiceChiavetta'";
                $conn->query($queryAggiornaSaldo);

                $queryAggiornaTotaleAcquistato = "UPDATE Utenti SET TotaleAcquisti = TotaleAcquisti + $importoAcquisto 
                                                WHERE CodiceChiavetta = '$codiceChiavetta'";
                $conn->query($queryAggiornaTotaleAcquistato);
                
                $queryAggiornaNumeroAcquisti = "UPDATE Utenti SET NumeroAcquisti = NumeroAcquisti + 1 
                                                WHERE CodiceChiavetta = '$codiceChiavetta'";
                $conn->query($queryAggiornaNumeroAcquisti);

                if ($idTransazione && $conn->affected_rows > 0) {
                    // Aggiorna il saldo nella sessione
                    $_SESSION['Saldo'] = $saldoAttuale - $importoAcquisto;
                    header("Location: ../client.php?display=In Erogazione");
                    exit();
                } else {
                    header("Location: ../client.php?error=ERRORE durante l'acquisto");
                    exit();
                }
            } else {
                header("Location: ../client.php?error=Saldo Insufficiente");
                exit();
            }
        } else {
            header("Location: ../client.php?error=ERRORE, saldo non disponibile");
            exit();
        }
    }

    // Funzione per ricaricare il saldo
    function modificaSaldo($codiceChiavetta, $importo) {
        global $conn;

        // Ottieni il saldo attuale dell'utente
        $querySaldo = "SELECT Saldo FROM Utenti WHERE CodiceChiavetta = '$codiceChiavetta'";
        $resultSaldo = $conn->query($querySaldo);

        if ($resultSaldo->num_rows > 0) {
            $saldoAttuale = $resultSaldo->fetch_assoc()['Saldo'];

            // Verifica che il saldo dopo la ricarica non sia inferiore a 0
            if ($saldoAttuale + $importo >= 0) {
                $queryTransazione = "INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo) 
                                    VALUES ('$codiceChiavetta', 'Ricarica', $importo)";
                $conn->query($queryTransazione);

                // Esegui la ricarica del saldo
                $queryAggiornaSaldo = "UPDATE Utenti SET Saldo = Saldo + $importo 
                                    WHERE CodiceChiavetta = '$codiceChiavetta'";
                $result = $conn->query($queryAggiornaSaldo);
                
                $queryAggiornaTotaleRicaricato = "UPDATE Utenti SET TotaleRicariche = TotaleRicariche + $importo
                                                WHERE CodiceChiavetta = '$codiceChiavetta'";
                $conn->query($queryAggiornaTotaleRicaricato);

                if ($result) {
                    // Aggiorna il saldo nella sessione
                    $_SESSION['Saldo'] = $saldoAttuale + $importo;
                    header("Location: ../client.php?success=Ricarica effettuata con successo");
                    exit();
                } else {
                    header("Location: ../client.php?error=Errore durante la ricarica del saldo");
                    exit();
                }
            } else {
                header("Location: ../client.php?error=ERRORE, ricarica non consentita");
                exit();
            }
        } else {
            header("Location: ../client.php?error=ERRORE, saldo non disponibile");
            exit();
        }
    }
?>