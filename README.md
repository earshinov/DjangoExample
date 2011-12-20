# DjangoExample

Очередная попытка использования Django.  Больше неудачная, чем удачная.

## Задание 1

Завести модель *динамического поля* (`Field`) и создать страницу для редактирования объектов этой модели.  Динамическое поле может быть:

  * текстовым
  * типа «дата»
  * типа «выбор из списка»
  * типа «министерство» (`ministry`)
  * типа «отрасль» (`sector`)

Для полей всех типов должны храниться:

  * таблица назначения («Компания» или «Контакт»)
  * человекопонятное название на русском и английском языках
  * название закладки (только латинские символы)
  * название поля (*field name*; только латинские символы)
  * признак обязательности заполнения поля (логическое значение)

\>>> **начало вставки**

**Разъяснение предметной области**: динамические поля — это колонки в базе данных, добавляемые операторами backoffice.  После создания динамического поля оператор может, к примеру, добавить поле в анкету, размещаемую на сайте и заполняемую посетителями.  Фактически, при создании динамического поля выполняется SQL-запрос `ALTER ... ADD COLUMN ...`, при удалении — соответственно, `ALTER ... DROP COLUMN`.  При этом:

  * Таблица назначения динамического поля определяет, в какую таблицу базы данных будет добавлена колонка
  * Название колонки берётся либо из *field name*, если он указан, либо из названия закладки
  * Тип данных колонки зависит от типа динамического поля

Касательно типа данных колонки, к примеру, для каждого поля типа «выбор из списка» заводится перечень элементов списка, и значение в колонке является ссылкой на таблицу элементов списка.

Всё это выходит за рамки того, что необходимо сделать в задании.  В задании необходимо лишь реализовать добавление / редактирование / удаление динамических полей, даже без выполнения инструкций `ALTER ...`.  Заведение элементов списка для полей типа «выбор из списка» можно выполнить в рамках **задания 2**.

\<<< **конец вставки**

Другие требования по заданию:

  * *Field name* динамического поля не должен быть доступен для редактирования через графический интерфейс.  Это будет просто способ задать название колонки в базе данных для *системных* динамических полей.  В рамках задания никаких специфических действий для обработки системных динамических полей выполнять не требуется.

  * Для текстовых динамических полей ко всему прочему должны храниться минимальная и максимальная длина вводимого текста.

  * Необходимо обеспечить уникальность заведённых в системе динамических полей, так чтобы на одну колонку базы данных не могло ссылаться более одного динамического поля.  Для этого необходимо проверять указанные для динамического поля таблицу назначения, название закладки, *field name*.

  * После создания динамического поля должно быть запрещено изменение таблицы назначения, типа динамического поля, названия закладки.  Это ограничение налагается для того, чтобы никогда не приходилось выполять `ALTER` после редактирования динамического поля, а только при создании и удалении.

  * Для выполнения задания **нельзя** использовать встроенную админку Django (потому что непонятно, как к ней прикрутить потом `ALTER`)

## Задание 2

Реализовать редактирование объектов, связанных отношением один-ко-многим (родительский-дочерний объект).  Дочерние объекты должны заводиться в виде списка на форме редактирования родительского объекта, при этом для каждого дочернего объекта должны редактироваться не менее двух полей.

В качестве одного из вариантов выполнения задания, можно реализовать заведение для динамических полей типа «выбор из списка» (см. **задание 1**) перечня элементов списка.

Для выполнения задания **можно** использовать встроенную админку Django.
