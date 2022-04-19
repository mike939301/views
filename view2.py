class ModerationTask(m_db.Model):
    """ Table with content on moderation or waiting for it."""

    __tablename__ = 'moderation_task'

    TYPE_LIVE = 'live'
    TYPE_COMMENT = 'comment'
    TYPE_MESSAGE = 'message'
    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'

    STATUS_NEW = 'new'
    STATUS_EMA = 'ema'
    STATUS_WAIT = 'wait'
    STATUS_MODERATION = 'mdr'

    CMT_TYPES = {TYPE_COMMENT, TYPE_MESSAGE}  # types for comments/messages from chat

    id = m_db.Column(m_db.Integer, primary_key=True)
    type = m_db.Column(m_db.String(16))
    comment_id = m_db.Column(m_db.BigInteger)
    video_id = m_db.Column(m_db.String(32))
    moderator_id = m_db.Column(m_db.Integer, default=0)
    status = m_db.Column(m_db.String(40))
    created_ts = m_db.Column(m_db.DateTime,  default=datetime.now)
    comment_state = m_db.Column(m_db.Text)

    @classmethod
    def get_tasks_with_comments_by_ids(cls, tasks_for_select: list) -> Select:
        """
        Build query for select tasks with comments by provided tasks_ids
        :param tasks_for_select: list of tasks for select
        :return: tasks sql query
        """
        return m_db.select(
            [ModerationTask.id.label('task_id'),
             ModerationTask.comment_id,
             Comment.user_id, Comment.video_id, Comment.text,
             Comment.date_added.label('created_ts')]
        ).select_from(
            ModerationTask.join(Comment, ModerationTask.comment_id == Comment.id)
        ).where(
            (Comment.state != Comment.STATE_DELETED) &
            ModerationTask.id.in_(tasks_for_select)
        ).order_by(
            ModerationTask.id.desc()
        )

    @classmethod
    def get_tasks_with_videos_by_ids(cls, tasks_for_select: list) -> Select:
        """
        Build query for select tasks with vieo_id by provided tasks_ids
        :param tasks_for_select: list of tasks for select
        :return: tasks sql query
        """
        return m_db.select(
            [ModerationTask.id.label('task_id'), ModerationTask.comment_id, ModerationTask.video_id,
             ModerationTask.moderator_id, ModerationTask.status]
        ).where(
            ModerationTask.id.in_(tasks_for_select)
        )

    @classmethod
    async def tasks_count_per_moderator_by_category(cls, moder_id, category=None):
        qs = m_db.select(
            [m_db.func.count(ModerationTask.id)]
        ).where(
            (ModerationTask.moderator_id == moder_id)
        )
        if category:
            qs = qs.where((ModerationTask.type == category))
        return await qs.gino.scalar()

    @classmethod
    def get_unattended_tasks(cls) -> Select:
        """
        Build query for select all unattended tasks
        :return: tasks sql query
        """
        return m_db.select([
            ModerationTask.id,
            ModerationTask.comment_id,
            ModerationTask.type,
            ModerationTask.video_id
        ]).where(
            (ModerationTask.moderator_id == 0) &
            (ModerationTask.status == ModerationTask.STATUS_WAIT)
        ).order_by(
            sa.case(
                [
                    (ModerationTask.type == ModerationTask.TYPE_COMMENT, '1'),
                    (ModerationTask.type == ModerationTask.TYPE_MESSAGE, '1'),
                    (ModerationTask.type == ModerationTask.TYPE_AUDIO, '2'),
                    (ModerationTask.type == ModerationTask.TYPE_VIDEO, '3'),
                    (ModerationTask.type == ModerationTask.TYPE_LIVE, '4')
                ], else_='0'
            ).desc(),
            ModerationTask.id.desc(),
        )

    @classmethod
    def get_unattended_tasks_by_type(cls, task_type: str) -> Select:
        """
        Build query for select all unattended tasks with specified task type
        :return: tasks sql query
        """
        return m_db.select([
            ModerationTask.id,
            ModerationTask.comment_id,
            ModerationTask.video_id
        ]).where(
            (ModerationTask.moderator_id == 0) &
            (ModerationTask.status == ModerationTask.STATUS_WAIT) &
            (ModerationTask.type == task_type)
        ).order_by(
            ModerationTask.id.desc(),
        )

    @classmethod
    def update_tasks(cls, moderator_id, limit, task_types) -> Select:
        """
        Build query for update and return task_ids
        :return: tasks sql query
        """
        tasks_to_update = m_db.select(
            [ModerationTask.id]
        ).where(
            (ModerationTask.moderator_id == moderator_id) &
            (ModerationTask.type.in_(task_types))
        ).order_by(ModerationTask.id.desc()).limit(limit)

        return m_db.update(ModerationTask).values(
            status=ModerationTask.STATUS_MODERATION
        ).where(
            ModerationTask.id.in_(tasks_to_update)
        ).returning(
            ModerationTask.id,
        )

