CREATE DATABASE IF NOT EXISTS adaptive_learning_db CHARACTER SET utf8mb4;
USE adaptive_learning_db;

-- 使用者資料表 [cite: 62]
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    UserName VARCHAR(100),
    Role ENUM('Student', 'Teacher')
);

-- 題目資料表 [cite: 62]
CREATE TABLE Questions (
    QuestionID INT AUTO_INCREMENT PRIMARY KEY,
    Content TEXT,
    Subject VARCHAR(50),
    CorrectAnswer TEXT,
    Tags VARCHAR(255)
);

-- 作答紀錄表 [cite: 62]
CREATE TABLE Answers (
    AnswerID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    QuestionID INT,
    UserAnswer TEXT,
    IsCorrect BOOLEAN,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID)
);

-- AI 錯誤分析表 [cite: 62]
CREATE TABLE AI_Analysis (
    AnalysisID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    QuestionID INT,
    ErrorType VARCHAR(100),
    Suggestion TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID)
);

-- 插入測試題目 [cite: 62]
INSERT INTO Questions (Content, Subject, CorrectAnswer, Tags) 
VALUES ('(-5) + (-3) = ?', 'Math', '-8', '負數運算');

INSERT INTO Questions (QuestionID, Content, Subject, CorrectAnswer, Tags) 
VALUES (1, '(-5) + (-3) = ?', 'Math', '-8', '負數運算');