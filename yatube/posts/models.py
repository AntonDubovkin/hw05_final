from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Формируем класс Group, котоырй содержит поля titile, slug, description
class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=200,
                             help_text='Заголовок группы'
                             )
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Описание групы'
                                   )

    class Meta:
        verbose_name = 'Заголовок'
        verbose_name_plural = 'Заголовки'

    # Добавляем метод для отображения инфомрации об обьекте класса.
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    # Добавляем внешний ключ к моедли User
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    # Добавляем внешний ключ к модели Group
    group = models.ForeignKey(
        Group,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой относится пост',
        blank=True,  # (Позволяет занести в поле пустое значение)
        null=True,  # (Будет хранить пустые значения)
        on_delete=models.SET_NULL,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'запись', 'Автор', 'пост'
        verbose_name_plural = 'записи', 'Авторы', 'посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='post',
        help_text='Комментарий')
    name = models.CharField(max_length=80)
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Оставьте свой комментарий здесь')
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE)
        # когда объект, на который имеется ссылка, удаляется,
        # все объекты, ссылающиеся на этот объект, также будут удалены
    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True)

    class Meta:
        ordering = ('created',)
        verbose_name_plural = 'Коментарии'
        verbose_name = 'Коментарий'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        # удобое читаемое имя в множественнои и единственном числе
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
