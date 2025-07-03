from .crud_user import user
from .crud_todo import todo

# 为了向后兼容，保留一些函数式接口别名
crud_user = user
crud_todo = todo

# 现在的使用方式：
# from app.crud import user, todo
#
# # 用户操作示例
# user_obj = await user.get(db, id=1)
# user_by_phone = await user.get_by_phone(db, phone="13800138000")
# new_user = await user.create(db, obj_in=UserCreate(...))
# updated_user = await user.update(db, db_obj=user_obj, obj_in=UserUpdate(...))
# deleted_user = await user.remove(db, id=1)
# authenticated_user = await user.authenticate(db, phone="...", password="...")
#
# # Todo 操作示例
# todo_obj = await todo.get(db, id=1)
# user_todos = await todo.get_by_owner(db, owner_id=1)
# new_todo = await todo.create_with_owner(db, obj_in=TodoCreate(...), owner_id=1)
# updated_todo = await todo.update(db, db_obj=todo_obj, obj_in=TodoUpdate(...))
# deleted_todo = await todo.remove(db, id=1)
