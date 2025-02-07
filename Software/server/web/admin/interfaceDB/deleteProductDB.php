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

    if ($_SERVER["REQUEST_METHOD"] == "GET") {
        if (isset($_GET['nomeProdotto'])) {
            $nomeProdotto = $_GET['nomeProdotto'];

            // Esegui la query di eliminazione
            $sqlEliminazione = "DELETE FROM Prodotti WHERE NomeProdotto = '$nomeProdotto'";
            
            if (!$conn->query($sqlEliminazione)) {
                header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore durante l\'eliminazione del prodotto');
                exit();
            }
        } else {
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: Nome del prodotto mancante');
            exit();
        }
    } else {
        header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: Richiesta non valida.');
        exit();
    }

    $conn->close();
    
    // Reindirizza alla pagina precedente
    header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Prodotto eliminato con successo');
    exit();
?>
