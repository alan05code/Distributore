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
    
    if (isset($_POST['nomeProdotto'])) {
        $nomeProdotto = $_POST['nomeProdotto'];

        // Esegui la query per ottenere il prezzo dal database
        $sql = "SELECT Prezzo FROM Prodotti WHERE NomeProdotto = '$nomeProdotto'";
        $result = $conn->query($sql);

        if ($result) {
            $row = $result->fetch_assoc();
            $prezzo = $row['Prezzo'];

            // Restituisci il prezzo in formato JSON
            echo json_encode(['Prezzo' => $prezzo]);
        } else {
            // Se la query non ha avuto successo, restituisci un messaggio di errore
            echo json_encode(['error' => 'Errore nella query']);
        }
    } else {
        // Se non è stata passata l'nomeProdotto, restituisci un messaggio di errore
        echo json_encode(['error' => 'NomeProdotto non fornito']);
    }

    $conn->close();
?>
