class WhiteTagView(HTTPMethodView):

    @doc.description("Add user to white list")
    @doc.produces({
        'status': doc.String()
    }, description='Result status', content_type='application/json')
    @auth_required(Moderator)
    async def put(self, request, user_id):
        user = await (await s_db.execute(ut.select().where(ut.c.id == user_id))).fetchone()

        if not user:
            return json_response({'status': 'Not found'}, status=404)

        if await UserBlackWhiteTag.get(user_id):
            await UserBlackWhiteTag.update.values(is_black=False).where(UserBlackWhiteTag.id == user_id).gino.status()
        else:
            await UserBlackWhiteTag.create(id=user_id, is_black=False)
        return json_response({'status': 'success'}, status=200)

    @doc.description("Remove user from white list")
    @doc.produces({
        'status': doc.String()
    }, description='Result status', content_type='application/json')
    @auth_required(Moderator)
    async def delete(self, request, user_id):
        user = await (await s_db.execute(ut.select().where(ut.c.id == user_id))).fetchone()

        if not user:
            return json_response({'status': 'Not found'}, status=404)

        await UserBlackWhiteTag.delete.where((UserBlackWhiteTag.id == user_id) & (UserBlackWhiteTag.is_black == False)) \
            .gino.status()
        return json_response({'status': 'success'}, status=200)


class BlackTagView(HTTPMethodView):

    @doc.description("Add user to black list")
    @doc.produces({
        'status': doc.String()
    }, description='Result status', content_type='application/json')
    @auth_required(Moderator)
    async def put(self, request, user_id):
        user = await (await s_db.execute(ut.select().where(ut.c.id == user_id))).fetchone()

        if not user:
            return json_response({'status': 'Not found'}, status=404)

        if await UserBlackWhiteTag.get(user_id):
            await UserBlackWhiteTag.update.values(is_black=True).where(UserBlackWhiteTag.id == user_id).gino.status()
        else:
            await UserBlackWhiteTag.create(id=user_id, is_black=True)
        return json_response({'status': 'success'}, status=200)

    @doc.description("Remove user from black list")
    @doc.produces({
        'status': doc.String()
    }, description='Result status', content_type='application/json')
    @auth_required(Moderator)
    async def delete(self, request, user_id):
        user = await (await s_db.execute(ut.select().where(ut.c.id == user_id))).fetchone()

        if not user:
            return json_response({'status': 'Not found'}, status=404)

        await UserBlackWhiteTag.delete.where((UserBlackWhiteTag.id == user_id) & (UserBlackWhiteTag.is_black == True)) \
            .gino.status()
        return json_response({'status': 'success'}, status=200)
