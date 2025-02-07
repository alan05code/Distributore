<?php
    session_start();

    // Termina la sessione
    session_destroy();

    // Reindirizza alla pagina di accesso
    header('Location: ../index.html');
    exit();
?>