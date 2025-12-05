CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nome VARCHAR(45),
    sexo VARCHAR(10),
    email VARCHAR(265)
);

CREATE TABLE exercicio (
    id_exercicio SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    musculos_trabalhados TEXT,
    video_execucao TEXT,
    imagem_musculos TEXT
);

CREATE TABLE avaliacao_fisica (
    id_avaliacao SERIAL PRIMARY KEY,
    idade INTEGER,
    peso INTEGER,
    altura INTEGER,
    nivel VARCHAR(20),
    frequencia INTEGER,
    doencas TEXT,
    limitacoes TEXT,
    id_usuario INTEGER NOT NULL,
    data_cadastro TIMESTAMP,
   
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE treino_dia (
    id_treino_dia SERIAL PRIMARY KEY
);

CREATE TABLE treino (
    id_treino SERIAL PRIMARY KEY,
    treino_A INTEGER,
    treino_B INTEGER,
    treino_C INTEGER,
    treino_D INTEGER,
    treino_E INTEGER,
    treino_F INTEGER,
    treino_G INTEGER,
    id_usuario INTEGER NOT NULL,

    FOREIGN KEY (treino_A) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_B) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_C) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_D) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_E) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_F) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (treino_G) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,

    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE item_treino (
    id_item_treino SERIAL PRIMARY KEY,
    series INTEGER,
    repeticoes INTEGER,
    intervalo INTEGER,
    
    id_treino_dia INTEGER NOT NULL, 
    id_exercicio INTEGER NOT NULL,

    FOREIGN KEY (id_treino_dia) REFERENCES treino_dia(id_treino_dia) ON DELETE CASCADE,
    FOREIGN KEY (id_exercicio) REFERENCES exercicio(id_exercicio) ON DELETE CASCADE
);