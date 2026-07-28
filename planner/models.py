from django.db import models

class User(models.Model):
    userName = models.CharField(max_length=80, unique=True, db_column='userName')
    userPW = models.CharField(max_length=120, db_column='userPW')
    userEmail = models.CharField(max_length=120, unique=True, db_column='userEmail')

    class Meta:
        db_table = 'tbUser'

    def __str__(self):
        return self.userName


class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID', related_name='subjects', null=True, blank=True)
    subjectName = models.CharField(max_length=50, db_column='subjectName')
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')

    class Meta:
        db_table = 'tbSubject'

    def __str__(self):
        return self.subjectName


class Item(models.Model):
    itemName = models.CharField(max_length=100, db_column='itemName')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subId', related_name='items')
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')

    class Meta:
        db_table = 'tbItem'

    def __str__(self):
        return self.itemName


class Scope(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='itemId', related_name='scopes')
    begin = models.IntegerField(db_column='begin')
    end = models.IntegerField(db_column='end')
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')

    class Meta:
        db_table = 'tbScope'


class LearningPlanList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID', related_name='learning_plans')
    learningPlanName = models.CharField(max_length=100, db_column='learningPlanName')
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')

    class Meta:
        db_table = 'tbLearningPlanList'

    def __str__(self):
        return self.learningPlanName


class TimeTableList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userID', related_name='time_table_lists', null=True, blank=True)
    timeTableName = models.CharField(max_length=100, db_column='timeTableName')
    learning_plan = models.ForeignKey(LearningPlanList, on_delete=models.CASCADE, db_column='learningPlanListID', related_name='time_tables', null=True, blank=True)
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')

    class Meta:
        db_table = 'tbTimeTableList'

    def __str__(self):
        return self.timeTableName


class TimeTable(models.Model):
    day = models.IntegerField(db_column='day')  # 0: 월요일, 1: 화요일, ...
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='itemId', related_name='time_tables')
    sTime = models.IntegerField(db_column='sTime')  # 분 단위 (0-1439)
    eTime = models.IntegerField(db_column='eTime')  # 분 단위 (0-1439)
    tag = models.CharField(max_length=200, blank=True, null=True, db_column='tag')
    time_table_list = models.ForeignKey(TimeTableList, on_delete=models.CASCADE, db_column='timeTableListId', related_name='time_tables')

    class Meta:
        db_table = 'tbTimeTable'
