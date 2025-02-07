<?php
    ob_start();

    // Connessione al database
    $servername = "localhost";
    $username = "webuser";
    $password = "pwd";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connessione fallita: " . $conn->connect_error);
    }

    // Verifica se sono stati inviati dati dal form
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        if(isset($_POST['annulla'])) {
            header('Location: ' . $_SERVER['HTTP_REFERER']);
            exit();
        }
        if (isset($_POST['update_button'])) {
            foreach ($_POST as $key => $value) {
                // Controlla se la chiave è relativa a uno slot di prodotto
                if (strpos($key, 'slot_') === 0) {
                    // Estrai il numero dello slot dal nome della chiave
                    $slot_number = substr($key, 5);
                    
                    // Estrai il nomeProdotto, prezzo e quantita corrispondente
                    $product_name = $_POST['product_cell_' . $slot_number];
                    if($product_name === "Vuoto") {
                        $product_price = 0;
                        $product_quantity = 0;
                    } else {
                        $product_price = $_POST['price_cell_' . $slot_number];
                        $product_quantity = $_POST['quantity_cell_' . $slot_number];
                    }

                    // Controlla se il nome del prodotto selezionato esiste nella tabella Prodotti
                    $check_product_query = "SELECT NomeProdotto FROM Prodotti WHERE NomeProdotto = '$product_name'";
                    $result_check_product = $conn->query($check_product_query);
                    if ($result_check_product->num_rows === 0) {
                        // header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore: Nome prodotto non valido');
                        // exit();
                        echo "$product_name";
                    }
        
                    // Aggiorna il record dello slot nel database
                    $update_query = "UPDATE ContenutoDistributore 
                                     SET NomeProdotto = '$product_name', Prezzo = '$product_price', Quantita = '$product_quantity' 
                                     WHERE Slot = '$slot_number'";
                    $conn->query($update_query);
                }
            }
            header('Location: ' . $_SERVER['HTTP_REFERER'] . '&success=Distributore aggioranto con successo');
            exit();
        }
    }

    $conn->close();

    header('Location: ' . $_SERVER['HTTP_REFERER'] . '&error=Errore. Riprova');
    exit();
?>