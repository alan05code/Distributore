<?php
    session_start();

    // Connessione al database
    $servername = "localhost";
    $username = "webuser";
    $password = "pwd";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    // Controlla la connessione al database
    if ($conn->connect_error) {
        die("Connessione al database fallita: " . $conn->connect_error);
    }

    // Gestione delle richieste di login
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $codiceChiavetta = $_POST['codiceChiavetta'];
        $pin = $_POST['pin'];

        $query = $conn->prepare("SELECT * FROM Utenti WHERE CodiceChiavetta = ? AND PIN = ?");
        $query->bind_param("ss", $codiceChiavetta, $pin);
        $query->execute();
        $result = $query->get_result();

        if ($result->num_rows == 1) {
            $row = $result->fetch_assoc();
            $_SESSION['CodiceChiavetta'] = $row['CodiceChiavetta'];
            $_SESSION['Nome'] = $row['Nome'];
            $_SESSION['Cognome'] = $row['Cognome'];
            $_SESSION['Saldo'] = $row['Saldo'];
            $_SESSION['NumeroAcquisti'] = $row['NumeroAcquisti'];

            header("Location: ../client.php?success=Loggato come " . $_SESSION['Nome'] . " " .$_SESSION['Cognome'] );
            exit();
        } else {
            header("Location: login.html?error=Credenziali errate. Riprova");
            exit();
        }
    }
?>