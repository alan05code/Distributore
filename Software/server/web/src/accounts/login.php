<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    if (isset($_POST['Client'])) {
        header("Location: ../../client/client.php");
        exit();
    }
    if (isset($_POST['Admin'])) {
        header("Location: ../../admin/login/login.html");
        exit();
    }

    header("Location: ../index.php?error=Errore. Riprova");
    exit();
}
?>
