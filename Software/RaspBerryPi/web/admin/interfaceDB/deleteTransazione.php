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

    // Verifica se l'ID della transazione è stato passato correttamente
    if (isset($_POST['idTransazione'])) {
        // Recupera l'ID della transazione dalla richiesta POST
        $idTransazione = $_POST['idTransazione'];

        // Prima elimina le righe corrispondenti nella tabella Dettaglitransazione
        $queryEliminazioneDettagli = "DELETE FROM Dettaglitransazione WHERE IDTransazione = $idTransazione";

        if (!$conn->query($queryEliminazioneDettagli)) {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore nella rimozione dei dettagli della transazione');
            exit();
        }

        // Prepara la query per la rimozione della transazione
        $queryRimozione = "DELETE FROM Transazioni WHERE IDTransazione = $idTransazione";

        // Esegui la query di rimozione
        if (!$conn->query($queryRimozione)) {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore nella rimozione della transazione');
            exit();
        }
    } else {
        header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=ID Prodotto inesistente');
        exit();
    }

    // Chiudi la connessione al database
    $conn->close();

    // Reindirizza alla pagina precedente dopo l'aggiornamento
    header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Transazione eliminata con successo');
    exit();
?>