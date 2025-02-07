<?php
    // inserisca questi USR e PSW per accedere alla sezione ADMIN
    $valid_username = 'admin';
    $valid_password = 'password';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $entered_username = $_POST['username'];
        $entered_password = $_POST['password'];

        if ($entered_username === $valid_username && $entered_password === $valid_password) {
            // Credenziali corrette, reindirizza a admin.php
            header('Location: ../admin.php?success=Loggato come ADMIN');
            exit();
        } else {
            header("Location: login.html?error=Credenziali errate. Riprova.");
            exit();
        }
    }
?>