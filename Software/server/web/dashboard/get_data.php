<?php
    $servername = "localhost";
    $username = "webuser";
    $password = "pwd";
    $dbname = "Distributore";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "SELECT cd.Slot, cd.NomeProdotto, cd.Prezzo, cd.Quantita, cd.Erogazione, p.Immagine AS ImmagineProdotto
            FROM ContenutoDistributore cd
            LEFT JOIN Prodotti p ON cd.NomeProdotto = p.NomeProdotto";
    $result = $conn->query($sql);

    $data = [];

    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
    }

    $conn->close();

    header('Content-Type: application/json');
    echo json_encode($data);
?>
