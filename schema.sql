-- ============================================================
-- FARMLINK POULTRY - Database Schema
-- AI-Enhanced Flock Management and Bird Identification System
-- ============================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS farmlink_db;
USE farmlink_db;

-- -----------------------------------------------------------
-- Table: flocks
-- Stores flock/batch information
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS flocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    total_initial_birds INT NOT NULL DEFAULT 0
);

-- -----------------------------------------------------------
-- Table: birds
-- Stores individual bird records identified by leg band number
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS birds (
    leg_band_number VARCHAR(50) PRIMARY KEY,
    flock_id INT NOT NULL,
    breed VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'Layer',
    hatch_date DATE NOT NULL,
    status ENUM('alive', 'dead', 'sold') NOT NULL DEFAULT 'alive',
    FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------
-- Table: health_records
-- Stores health observations, diseases, and treatments
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    leg_band_number VARCHAR(50) NOT NULL,
    record_date DATE NOT NULL,
    disease VARCHAR(200) DEFAULT NULL,
    treatment VARCHAR(200) DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    FOREIGN KEY (leg_band_number) REFERENCES birds(leg_band_number) ON DELETE CASCADE
);
