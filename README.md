# DjangoExample

Выдуманное задание по Django

## Мини-ТЗ

### Задание 1

Завести модель *динамического поля* (`Field`) и создать страницу для редактирования объектов этой модели.  Использовать возможность встроенной админки Django не допускается.

Динамическое поле может быть:

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

  * Для текстовых динамических полей ко всему прочему должны храниться минимальная и максимальная длина вводимого текста.  Контролы для ввода этих параметров не должны отображаться, если редактируемое динамическое поле не типа «текст».

  * Необходимо обеспечить уникальность заведённых в системе динамических полей, так чтобы на одну колонку базы данных не могло ссылаться более одного динамического поля.  Для этого необходимо проверять указанные для динамического поля таблицу назначения, название закладки, *field name*.

  * После создания динамического поля должно быть запрещено изменение таблицы назначения, типа динамического поля, названия закладки.  Это ограничение налагается для того, чтобы никогда не приходилось выполять `ALTER` после редактирования динамического поля, а только при создании и удалении.

### Задание 2

Реализовать редактирование объектов, связанных отношением один-ко-многим (родительский-дочерний объект).  Дочерние объекты должны заводиться в виде списка на форме редактирования родительского объекта, при этом для каждого дочернего объекта должны редактироваться не менее двух полей.

В качестве одного из вариантов выполнения задания, можно реализовать заведение для динамических полей типа «выбор из списка» (см. **задание 1**) перечня элементов списка.

### Задание 3

Выполнить локализацию интерфейса на английский и русский языки.  Пользователю должна быть предоставлена страница для выбора предпочтительного языка.

## Прогресс выполнения заданий

На данный момент выполнены все задания.  Кроме собственно выполнения заданий, много времени ушло на кодирование мелочей, в том числе тех, которые потенциально могли бы поддерживаться из коробки, и исправление мелких аспектов поведения Django, которые мне кажутся неправильными.  Чуть более подробно об этих мелочах написано в соответствующем подразделе ниже.

Зависимости проекта:

  * Python (тестировалось на версии 2.7)
  * Django (тестировалось на версии 1.3.1)
  * [django-easymode][] (тестировалось на версии 1.0b1).  Пакет используется ради средств интернационализации [django-easymode.i18n][]
  * [django-rosetta][] (тестировалось на версии 0.6.2).  Пакет необходим для [django-easymode.i18n][]
  * [django-debug-toolbar][]

### Советы касательно разработки на Django

  * Eclipse + PyDev — довольно вменяемая IDE.  Единственная значимая проблема — [Go to arbitrary module source\?][1].  Чтобы, используя сочетание клавиш Ctrl-Shift-T, можно было переходить к объявлениям классов из Django, необходимо добавить каталог Django (например, `/usr/lib/python2.7/site-packages/django/`) в список source folders проекта.  Для этого открыть окно свойств проекта > пункт *Pydev - PYTHONPATH* > вкладка *External Libraries* > нажать кнопку *Add source folder*.

  * Чтобы отслеживать выполняемые Django SQL-запросы во время отладки, достаточно поставить точку останова внутрь метода `SQLCompiler.executeSQL` в пакете `django.db.models.sql.compiler`.

### Подробности реализации задания 2

В рамках задания 2 реализовано заведение пунктов списка для динамических полей типа «выбор из списка».  Для реализации использованы т.н. inline formsets.  Ссылки по теме:

  * [How to have a nested inline formset within a form in Django?][formsets1]
  * [Model formsets][formsets2] в официальной документации Django
  * Общая статья о [Formsets][formsets3] в официальной документации

Интерфейс, реализуемый inline formsets, легко получить и во встроенной админке Django.  А именно, [One-to-many inline select with Django admin][formsets4]

При просмотре выполняемых Django SQL-запросов выяснилось, что при сохранении формсета каждая существующая запись в нём выбирается из базы данных дважды: один раз, естественно, для заполнения формсета, а второй… без какой-либо пользы.  Повторное выполнение запроса `SELECT` происходит в методе `BaseModelFormSet.save_existing_objects`, где получается значение первичного ключа:

    raw_pk_value = form._raw_value(pk_name)

    # clean() for different types of PK fields can sometimes return
    # the model instance, and sometimes the PK. Handle either.
    pk_value = form.fields[pk_name].clean(raw_pk_value)
    pk_value = getattr(pk_value, 'pk', pk_value)

Объект `form.fields[pk_name]` является экземпляром класса `ModelChoiceField`, чей метод `clean` посредством другого метода `to_python` загружает по указанному значению первичного ключа объект из базы (!).  И всё это делается для того, чтобы у результирующего объекта снова получить значение первичного ключа (!).  К сожалению, нормальным способом переопределить этот код не получается, поэтому пока оставил всё как есть.

### Что реализовано из мелочей

  * Отсутствующие в Django **примечания для полей**, в том числе относящиеся к валидации.  К примеру, добавляя в коллекцию валидаторов поля наш валидатор `LatinCharsValidator`, мы обеспечиваем, что на веб-странице у этого поля пользователь увидит подсказку о том, что в поле нужно вводить только латинские символы.  Реализация потребовала вмешательства в классы полей моделей и полей форм (в виде создания хитрых обёрток для них) и создания шаблончика формы.

  * Использование для полей опции **`null=True`** по умолчанию.  Мне кажется, пустое значение в контроле должно приравниваться к отсутствию значения.  Это реализовано на уровне тех же обёрток для классов полей.

  * Django при сохранении в базу записи, которой проставлено значение первичного ключа (ID), отдельным SQL-запросом (!) проверяет, что запись уже существует в базе.  Мне это кажется избыточным, поэтому я предусмотрел свой базовый класс модели, где при сохранении записи с ID выставляю флажок **`force_update=True`**.

Список не претендует на полноту.


[django-easymode]: http://pypi.python.org/pypi/django-easymode/
[django-easymode.i18n]: http://packages.python.org/django-easymode/i18n/api.html
[django-rosetta]: http://pypi.python.org/pypi/django-rosetta/
[django-debug-toolbar]: https://github.com/django-debug-toolbar/django-debug-toolbar#readme

[formsets1]: http://stackoverflow.com/questions/5518826/
[formsets2]: https://docs.djangoproject.com/en/1.3/topics/forms/modelforms/#model-formsets
[formsets3]: https://docs.djangoproject.com/en/1.3/topics/forms/formsets/
[formsets4]: http://stackoverflow.com/questions/6034047/

[1]: http://stackoverflow.com/questions/7392461/
