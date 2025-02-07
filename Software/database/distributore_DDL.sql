-- DDL

DROP DATABASE IF EXISTS Distributore; 
CREATE DATABASE Distributore; 
USE Distributore;

-- Creazione della tabella Utenti
CREATE TABLE Utenti (
	CodiceChiavetta VARCHAR(8) PRIMARY KEY NOT NULL,
	PIN INT DEFAULT 1234,
	Nome VARCHAR(50),
	Cognome VARCHAR(50),
	Saldo DECIMAL(10, 2) DEFAULT 0,
	NumeroAcquisti INT DEFAULT 0,
	TotaleAcquisti DECIMAL(10, 2) DEFAULT 0,
	TotaleRicariche DECIMAL(10, 2) DEFAULT 0
);

-- Creazione della tabella Prodotti
CREATE TABLE Prodotti (
	NomeProdotto VARCHAR(50) PRIMARY KEY NOT NULL,
	Prezzo DECIMAL(10, 2),
	QuantitaDisponibile INT,
	Immagine VARCHAR(255) DEFAULT '../dashboard/products/no-image.png',
	QuantitaVenduta INT DEFAULT 0
);

-- Creazione della tabella Transazioni
CREATE TABLE Transazioni (
	IDTransazione INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	CodiceChiavetta VARCHAR(8),
	TipoTransazione VARCHAR(8),
	Importo DECIMAL(10, 2),
	Quantita INT DEFAULT 1,
	FOREIGN KEY (CodiceChiavetta) REFERENCES Utenti(CodiceChiavetta)
);

-- Creazione della tabella DettagliTransazione
CREATE TABLE Dettaglitransazione (
	IDTransazione INT PRIMARY KEY NOT NULL,
	NomeProdotto VARCHAR(50),
	FOREIGN KEY (IDTransazione) REFERENCES Transazioni(IDTransazione),
	FOREIGN KEY (NomeProdotto) REFERENCES Prodotti(NomeProdotto)
);

-- Creazione della tabella ContenutoDistributore
CREATE TABLE ContenutoDistributore (
	Slot INT PRIMARY KEY NOT NULL,
	NomeProdotto VARCHAR(50) NOT NULL,
	Prezzo DECIMAL(10, 2),
	Quantita INT,
	Immagine VARCHAR(255),
	Erogazione BOOLEAN DEFAULT 0,
	FOREIGN KEY (NomeProdotto) REFERENCES Prodotti(NomeProdotto) ON DELETE CASCADE
);

CREATE TABLE Statistiche (
	Dates DATE PRIMARY KEY NOT NULL,
	GuadagnoTotale DECIMAL(10, 2), 
	BestSellerID VARCHAR(50)
);
-- BestSeller Da implementare 