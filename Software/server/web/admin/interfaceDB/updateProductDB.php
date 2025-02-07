<?php
    ob_start();

    //Connessione al database
    $servername = "localhost";
    $username = "webuser";
    $password = "pwd";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die('Connessione fallita: ' . $conn->connect_error);
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $nomeProdotto = $_POST['nomeProdotto'];
        $nuovaQuantita = $_POST['nuovaQuantita'];
        $nuovoPrezzo = $_POST['nuovoPrezzo'];

        if (isset($_FILES["immagineProdotto"])) {
            $nomeProdotto = $_POST["nomeProdotto"];
            $uploadDirectory = "../dashboard/products/";
            $nomeFile = basename($_FILES["immagineProdotto"]["name"]);
            if ($nomeFile != "") {
                $immagine = $uploadDirectory . $nomeFile;

                $sqlUpdateProdotto = "UPDATE Prodotti 
                                        SET QuantitaDisponibile = $nuovaQuantita, 
                                            Prezzo = $nuovoPrezzo, 
                                            Immagine = '$immagine'
                                        WHERE NomeProdotto = '$nomeProdotto'";
            } else {
                $sqlUpdateProdotto = "UPDATE Prodotti 
                                        SET QuantitaDisponibile = $nuovaQuantita, 
                                            Prezzo = $nuovoPrezzo
                                        WHERE NomeProdotto = '$nomeProdotto'";
            }

            $conn->query($sqlUpdateProdotto);

            if (!$conn->query($sqlUpdateProdotto)) {
                header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore durante l\'aggiornamento del Prodotto');
                exit();
            }
    
            $conn->close();
        } else {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore nella lettura del file Immagine');
            exit();
        }

        // Reindirizza alla pagina precedente dopo l'aggiornamento
        header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Prodotto aggiornato con successo');
        exit();
    }
?>