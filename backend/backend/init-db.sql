-- Script de inicialização do banco MySQL
-- Executado automaticamente na primeira vez que o container sobe

-- Garante charset UTF-8
ALTER DATABASE sos_pets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Concede privilégios ao usuário
GRANT ALL PRIVILEGES ON sos_pets.* TO 'sos_user'@'%';
FLUSH PRIVILEGES;

-- Mensagem de sucesso
SELECT 'Database initialized successfully!' AS message;
