from django.db import migrations, models
import django.db.models.deletion

def create_equipment_and_migrate_data(apps, schema_editor):
    Object = apps.get_model('LIFTEH', 'Object')
    EquipmentModel = apps.get_model('LIFTEH', 'EquipmentModel')
    
    # 1. Создаем EquipmentModel для всех уникальных моделей
    unique_models = Object.objects.exclude(model__isnull=True).exclude(model='').values_list('model', flat=True).distinct()
    
    model_mapping = {}
    for model_name in unique_models:
        equipment_model, created = EquipmentModel.objects.get_or_create(
            name=model_name,
            defaults={'folder_id': ''}
        )
        model_mapping[model_name] = equipment_model

def reverse_migration(apps, schema_editor):
    pass  # При отмене миграции ничего не делаем

class Migration(migrations.Migration):
    dependencies = [
        ('LIFTEH', '0007_object_folder_id'),
    ]

    operations = [
        # 1. Создаем модель EquipmentModel
        migrations.CreateModel(
            name='EquipmentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название модели')),
                ('folder_id', models.CharField(max_length=50, verbose_name='ID папки Яндекс.Диска')),
            ],
            options={
                'verbose_name': 'Модель оборудования',
                'verbose_name_plural': 'Модели оборудования',
                'ordering': ['name'],
            },
        ),
        
        # 2. Добавляем временное ForeignKey поле
        migrations.AddField(
            model_name='object',
            name='model_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='LIFTEH.equipmentmodel'),
        ),
        
        # 3. Заполняем данные
        migrations.RunPython(create_equipment_and_migrate_data, reverse_migration),
        
        # 4. Удаляем старое поле model
        migrations.RemoveField(
            model_name='object',
            name='model',
        ),
        
        # 5. Переименовываем временное поле
        migrations.RenameField(
            model_name='object',
            old_name='model_temp',
            new_name='model',
        ),
        
        # 6. Удаляем folder_id из Object
        migrations.RemoveField(
            model_name='object',
            name='folder_id',
        ),
    ]