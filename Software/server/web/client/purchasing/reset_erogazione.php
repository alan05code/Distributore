<?php
    if(isset($_POST['slot'])) {
        // Connessione al database
        $servername = "localhost";
        $username = "root";
        $password = "";
        $dbname = "Distributore";

        $conn = new mysqli($servername, $username, $password, $dbname);

        if ($conn->connect_error) {
            die("Connessione fallita: " . $conn->connect_error);
        }
        
        $slot = $_POST['slot'];
        $sql = "UPDATE ContenutoDistributore SET Erogazione = 0 WHERE Slot = '$slot'";
        if ($conn->query($sql) === TRUE) {
            $conn->close();
            header("Location: ../client.php?success=Acquisto effettuato con successo");
            exit();
        } else {
            $conn->close();
            header("Location: ../client.php?error=Errore durante l'erogazione");
            exit();
        }
    }
?>
