-- DML

INSERT INTO Utenti (CodiceChiavetta, PIN, Nome, Cognome, Saldo, NumeroAcquisti) VALUES
('1A4001', 1234, 'Pietro', 'T', 10.25, 4),
('2aebaeae', 1234, 'Michele', 'Barbon', 5.00, 0);

INSERT INTO Prodotti (NomeProdotto, Prezzo, QuantitaDisponibile, QuantitaVenduta, Immagine) VALUES
('Vuoto', 0, 0, 0, '../dashboard/products/no-image.png'),

('Brioche', 1.20, 50, 0, '../dashboard/products/brioche.png'),
('Cracker', 0.35, 75, 9, '../dashboard/products/cracker.png'),
('Barretta', 1.25, 30, 0, '../dashboard/products/barretta-di-cioccolato.png'),
('Ringo', 0.75, 60, 3, '../dashboard/products/ringo.png'),
('Patatine', 0.55, 40, 10, '../dashboard/products/patatine.png'),
('Oreo', 0.60, 25, 5, '../dashboard/products/oreo.png'),
('Pepsi', 0.45, 50, 4, '../dashboard/products/pepsi.png'),
('Acqua Lete', 0.30, 100, 15, '../dashboard/products/acqua-lete.png'),
('Tramezzino', 1.55, 100, 2, '../dashboard/products/tramezzino.png');

INSERT INTO Transazioni (IDTransazione, CodiceChiavetta, TipoTransazione, Importo) VALUES
(1, '1A4001', 'Ricarica', 15.00),
(2, '1A4001', 'Acquisto', 4.75);


INSERT INTO Statistiche (Dates, GuadagnoTotale, BestSellerID) VALUES 
('2023-01-01', 0, 000000);

INSERT INTO contenutoDistributore (Slot, NomeProdotto, Prezzo, Quantita) VALUES 
(1, 'Brioche', 1.20, 10),
(2, 'Cracker', 0.35, 4),
(3, 'Acqua Lete', 0.30, 5),
(4, 'Vuoto', 0.00, 0),
(5, 'Ringo', 0.75, 2),
(6, 'Patatine', 0.55, 0),
(7, 'Oreo', 0.60, 7),
(8, 'Pepsi', 0.45, 4),
(9, 'Vuoto', 0.00, 0);