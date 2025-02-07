<?php
    ob_start();
    
    //Connessione al database
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die('Connessione fallita: ' . $conn->connect_error);
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST") {

        // Verifica che i dati del modulo siano stati inviati
        if (
            isset($_POST['nuovoNomeProdotto']) &&
            isset($_POST['nuovaQuantita']) &&
            isset($_POST['nuovoPrezzo'])
        ) {
            // Ottieni i dati dal modulo
            $nuovoNomeProdotto = $_POST['nuovoNomeProdotto'];
            $nuovaQuantita = $_POST['nuovaQuantita'];
            $nuovoPrezzo = $_POST['nuovoPrezzo'];

            if (isset($_FILES["immagineProdotto"])) {
                $uploadDirectory = "../dashboard/products/";
                $nomeFile = basename($_FILES["immagineProdotto"]["name"]);
                if ($nomeFile != "") {
                    $nuovaImmagine = $uploadDirectory . $nomeFile;
                    $sqlInserimento = "INSERT INTO Prodotti (NomeProdotto, QuantitaDisponibile, Prezzo, Immagine) VALUES ('$nuovoNomeProdotto', $nuovaQuantita, $nuovoPrezzo, '$nuovaImmagine')";
                } else {
                    $sqlInserimento = "INSERT INTO Prodotti (NomeProdotto, QuantitaDisponibile, Prezzo) VALUES ('$nuovoNomeProdotto', $nuovaQuantita, $nuovoPrezzo)";
                }

                if (!$conn->query($sqlInserimento)) {
                    header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: inserimento del prodotto non riuscito');
                    exit();
                }

                // Chiudi la connessione al database
                $conn->close();
            } else {
                header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore nella lettura del file Immagine');
                exit();
            }  
        } else {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: Dati del modulo mancanti');
            exit();
        }
    } else {
        header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: Richiesta non valida');
        exit();
    }

    // Reindirizza alla pagina precedente dopo l'aggiornamento
    header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Nuovo prodotto inserito con successo');
    exit();
?>
