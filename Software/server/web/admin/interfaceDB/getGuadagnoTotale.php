<?php
    ob_start();

    // Connessione al database
    $servername = "localhost";
    $username = "webuser";
    $password = "pwd";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die('Connessione fallita: ' . $conn->connect_error);
    }

    $guadagnoTotale = createNewGT();
    $bestSeller = researchBestSellerID(); // Correggi il nome della variabile
    aggiornaGuadagnoTotale($guadagnoTotale, $bestSeller); // Passa la variabile corretta

    $conn->close();

    // Funzione per calcolare il guadagno totale
    function createNewGT() {
        global $conn;

        $sql = "SELECT SUM(Importo * Quantita) AS GuadagnoTotale 
                FROM Transazioni
                WHERE TipoTransazione = 'Acquisto'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $guadagnoTotale = $row["GuadagnoTotale"];
            return $guadagnoTotale;
        } else {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore durante il calcolo del guadagno totale');
            exit();
        }
    }

    // Funzione per trovare il best seller
    function researchBestSellerID() {
        global $conn;

        $sql = "SELECT NomeProdotto FROM Prodotti ORDER BY QuantitaVenduta DESC LIMIT 1";
        $bestSellerResult = $conn->query($sql);

        if ($bestSellerResult->num_rows > 0) {
            $row = $bestSellerResult->fetch_assoc();
            return $row["NomeProdotto"]; // Restituisci il nome del prodotto
        } else {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore durante il calcolo del best seller');
            exit();
        }
    }

    // Funzione per aggiornare il guadagno totale
    function aggiornaGuadagnoTotale($guadagnoTotale, $bestSeller) {
        global $conn;
        $dataAttuale = date("Y-m-d");

        try {
            $checkExistingQuery = "SELECT * FROM Statistiche WHERE Dates = '$dataAttuale'";
            $existingResult = $conn->query($checkExistingQuery);

            if ($existingResult->num_rows > 0) {
                $updateQuery = "UPDATE Statistiche SET GuadagnoTotale = '$guadagnoTotale', BestSellerID = '$bestSeller' WHERE Dates = '$dataAttuale'";
                $conn->query($updateQuery);
            } else {
                $insertQuery = "INSERT INTO Statistiche (Dates, GuadagnoTotale, BestSellerID) VALUES ('$dataAttuale', '$guadagnoTotale', '$bestSeller')";
                $conn->query($insertQuery);
            }

            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Guadagno Totale aggiornato con successo');
            exit();
        } catch (Exception $e) {
            echo "Errore durante l'aggiornamento o l'inserimento del guadagno totale: " . $e->getMessage();
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore, guadagno totale non aggiornato');
            exit();
        }
    }
?>