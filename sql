DECLARE @SearchStr NVARCHAR(100) = 'еуые';
DECLARE @SQL NVARCHAR(MAX) = '';

SELECT @SQL = @SQL + 
    'IF EXISTS (SELECT 1 FROM ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) +
    ' WHERE ' + QUOTENAME(c.name) + ' LIKE ''%' + @SearchStr + '%'')' + CHAR(13) + CHAR(10) +
    'BEGIN' + CHAR(13) + CHAR(10) +
    '    PRINT ''Найдено в таблице ' + s.name + '.' + t.name + ', колонка ' + c.name + '''' + CHAR(13) + CHAR(10) +
    'END;' + CHAR(13) + CHAR(10)
FROM sys.schemas s
INNER JOIN sys.tables t ON s.schema_id = t.schema_id
INNER JOIN sys.columns c ON t.object_id = c.object_id
INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
WHERE ty.name IN ('char', 'varchar', 'nchar', 'nvarchar', 'text', 'ntext');

EXEC sp_executesql @SQL;



-------------------------------------------
DECLARE @SearchStr NVARCHAR(100) = 'тест';
DECLARE @ReplaceStr NVARCHAR(100) = 'test';
DECLARE @SQL NVARCHAR(MAX) = '';

SELECT @SQL = @SQL +
    'IF EXISTS (SELECT 1 FROM ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) +
    ' WHERE ' + QUOTENAME(c.name) + ' LIKE ''%' + @SearchStr + '%'')' + CHAR(13) + CHAR(10) +
    'BEGIN' + CHAR(13) + CHAR(10) +
    '    PRINT ''Обновление ' + s.name + '.' + t.name + ', колонка ' + c.name + ''';' + CHAR(13) + CHAR(10) +
    '    UPDATE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) +
    ' SET ' + QUOTENAME(c.name) + ' = REPLACE(' + QUOTENAME(c.name) + ', ''' + @SearchStr + ''', ''' + @ReplaceStr + ''')' +
    ' WHERE ' + QUOTENAME(c.name) + ' LIKE ''%' + @SearchStr + '%'';' + CHAR(13) + CHAR(10) +
    'END;' + CHAR(13) + CHAR(10)
FROM sys.schemas s
INNER JOIN sys.tables t ON s.schema_id = t.schema_id
INNER JOIN sys.columns c ON t.object_id = c.object_id
INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
WHERE ty.name IN ('char', 'varchar', 'nchar', 'nvarchar', 'text', 'ntext');

-- Вывод сгенерированного скрипта для проверки:
PRINT @SQL;

-- Для выполнения обновлений раскомментируйте следующую строку:
-- EXEC sp_executesql @SQL;
