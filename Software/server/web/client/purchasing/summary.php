<?php
    session_start();
    ob_start();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Riepilogo Ordine</title>
    <link rel="stylesheet" href="../../src/style.css">
</head>
<body>
    <?php
        function printSummary($nomeProdotto, $quantita, $prezzoTotale, $prezzo) {
            $output = '<h2>Riepilogo Ordine</h2>';
            $output .= '<h4>Saldo Attuale: '. $_SESSION['Saldo'] .'€</h4>
                        <br>';

            $output .= '<table border="1">
                        <tr>
                            <th>Nome Articolo</th>
                            <th>Quantità</th>
                            <th>Importo</th>
                        </tr>
                        <tr>
                            <td>'. $nomeProdotto . '</td>
                            <td>'. $quantita .'</td>
                            <td>'. $prezzoTotale .'€</td>
                        </tr>
                    </table>
                    <br>';

            $output .= '<form method="post" action="../functions/functions.php">
                            <input type="hidden" name="nomeProdotto" value="' . $nomeProdotto . '">
                            <input type="hidden" name="prezzo" value="' . $prezzo . '">
                            <input type="hidden" name="quantita" value="' . $quantita . '" required>
                            <input type="submit" name="confermaOrdine" value="Conferma">
                            <input type="submit" name="annullaOrdine" value="Annulla">
                        </form>';

            return $output;
        }
    ?>
</body>
</html>

<?php
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        if (isset($_POST['acquista'])) {
            $nomeProdotto = $_POST["nomeProdotto"];
            $nomeProdotto = $_POST["nomeProdotto"];
            $quantita = $_POST["quantita"];
            $prezzo = $_POST["prezzo"];
            $prezzoTotale = $prezzo * $quantita;

            if($_SESSION["Saldo"] > $prezzoTotale) {
                echo printSummary($nomeProdotto, $quantita, $prezzoTotale, $prezzo);
            } else {
                header("Location: ../client.php?error=Saldo Insufficente");
                exit();
            }
            
        }
    }
?>