
import pytest
import uuid
import copy
from unittest.mock import patch
from io import BytesIO
from werkzeug.datastructures import FileStorage
from flask import url_for,make_response,json,current_app

from invenio_accounts.testutils import login_user_via_session
from invenio_pidstore.models import PersistentIdentifier
from weko_admin.models import BillingPermission
from weko_records.models import ItemMetadata, ItemTypeProperty
from weko_records.api import Mapping
from weko_records_ui.models import RocrateMapping
from weko_workflow.models import WorkFlow, FlowDefine

from tests.helpers import login

def assert_statuscode_with_role(response,is_admin,error_code=403):
    if is_admin:
        assert response.status_code != error_code
    else:
        assert response.status_code == error_code
# class ItemTypeMetaDataView(BaseView):
class TestItemTypeMetaDataView:

#     def index(self, item_type_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_index_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_index_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client=client,email=users[index]["email"])
        url = url_for("itemtypesregister.index")
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
        url = url_for("itemtypesregister.index",item_type_id=10)#
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_index(self,client,admin_view,item_type,users):
        login_user_via_session(client=client,email=users[0]["email"])
        url = url_for("itemtypesregister.index",item_type_id=3)
        with patch("weko_itemtypes_ui.admin.ItemTypeMetaDataView.render",return_value=make_response()) as mock_render:
            res = client.get(url)
            assert res.status_code == 200#
            itemtype_list_ = [(obj["item_type_name"],obj["item_type_name"].name,obj["item_type"].id,obj["item_type"].harvesting_type,obj["item_type"].is_deleted,obj["item_type"].tag) for obj in item_type]
            itemtype_list = sorted(itemtype_list_, key=lambda x: x[2])
            mock_render.assert_called_with(
                'weko_itemtypes_ui/admin/create_itemtype.html',
                item_type_list=itemtype_list,
                id=3,
                is_sys_admin=True,
                lang_code="en",
                uiFixedProperties=current_app.config['WEKO_ITEMTYPES_UI_FIXED_PROPERTIES'],
                ui_pubdate_titles=current_app.config['WEKO_ITEMTYPES_UI_PUBDATE_DEFAULT_TITLES']
            )
#     def render_itemtype(self, item_type_id=0):
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_render_itemtype_acl(self,client,admin_view,users,item_type,index,is_permission):
        login_user_via_session(client=client,email=users[index]["email"])
        url = url_for("itemtypesregister.render_itemtype",item_type_id=2)
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_render_itemtype -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_render_itemtype(self,client,admin_view,item_type,users,):
        login_user_via_session(client=client,email=users[0]["email"])

        url = url_for("itemtypesregister.render_itemtype",item_type_id=2)
        res = client.get(url)
        result = json.loads(res.data)
        assert result["edit_notes"] == {}
        assert result["table_row"] != []
        assert result["meta_list"] != {}


#     def delete_itemtype(self, item_type_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_delete_itemtype -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_delete_itemtype(self,client,admin_view,db,users,item_type):
        login_user_via_session(client=client,email=users[0]["email"])
        with patch("weko_workflow.utils.get_cache_data", return_value=False):
            url = url_for("itemtypesregister.delete_itemtype")
            res = client.post(url)
            assert json.loads(res.data)["code"] == -1

            url = url_for("itemtypesregister.delete_itemtype",item_type_id=100)
            res = client.post(url)
            assert json.loads(res.data)["code"] == -1

            url = url_for("itemtypesregister.delete_itemtype",item_type_id=1)
            with patch("weko_itemtypes_ui.admin.flash") as mock_flash:
                res = client.post(url)
                mock_flash.assert_called_with("Cannot delete Item type for Harvesting.","error")
                assert json.loads(res.data)["code"] == -1

            item_type1 = item_type[0]["item_type"]
            item_type1.harvesting_type = False
            item_type2 = item_type[1]["item_type"]
            item_type2.harvesting_type = False
            db.session.merge(item_type1)
            db.session.merge(item_type2)
            item = ItemMetadata(item_type_id=item_type1.id,json={})

            db.session.add(item)
            db.session.commit()
            pid = PersistentIdentifier(
                pid_type="recid",
                pid_value="1",
                status="R",
                object_type="rec",
                object_uuid=item.id
            )
            db.session.add(pid)
            db.session.commit()
            with patch("weko_itemtypes_ui.admin.flash") as mock_flash:
                url = url_for("itemtypesregister.delete_itemtype",item_type_id=item_type1.id)
                res = client.post(url)
                mock_flash.assert_called_with("Cannot delete due to child existing item types.","error")
                assert json.loads(res.data)["code"] == -1#

        with patch("weko_workflow.utils.get_cache_data", return_value=True):
            with patch("weko_itemtypes_ui.admin.flash") as mock_flash:
                url = url_for("itemtypesregister.delete_itemtype",item_type_id=item_type2.id)
                res = client.post(url)
                mock_flash.assert_called_with("Item type cannot be deleted becase import is in progress.","error")
                assert json.loads(res.data)["code"] == -1

        with patch("weko_workflow.utils.get_cache_data", return_value=False):
            with patch("weko_itemtypes_ui.admin.flash") as mock_flash:
                url = url_for("itemtypesregister.delete_itemtype",item_type_id=item_type2.id)
                res = client.post(url)
                mock_flash.assert_called_with("Deleted Item type successfully.")
                assert json.loads(res.data)["code"] == 0

# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_register_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
#     def register(self, item_type_id=0):
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_register_acl(self,client,admin_view,users,item_type,index,is_permission):
        login_user_via_session(client=client,email=users[index]["email"])
        url = url_for("itemtypesregister.register",item_type_id=1)
        with patch('weko_workflow.utils.get_cache_data', return_value=True):
            res = client.post(url,json={})
            if is_permission:
                assert res.status_code == 400
                result = json.loads(res.data)
                assert result["msg"] == 'Item type cannot be updated because import is in progress.'
            else:
                assert res.status_code == 403

# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_register -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_register(self,app,client,db,admin_view,users, item_type):
        login_user_via_session(client=client,email=users[0]["email"])
        login(app,client,obj=users[0]["obj"])

        with patch("weko_records.api.after_record_insert.send"):
            with patch("weko_records.api.before_record_insert.send"):
                with patch("weko_workflow.utils.get_cache_data", return_value=False):

                    # Content-Type is not 'application/json'
                    url = url_for("itemtypesregister.register")
                    res = client.post(url,headers={"Content-Type":"plain/text"})
                    assert json.loads(res.data)["msg"] == "Header Error"

                    data = {
                        "table_row_map":{
                            "schema":{"object":"test schema"},
                            "form":["test form"],
                            "name":"new item type name",
                        }
                    }
                    schema = copy.deepcopy(data["table_row_map"]["schema"])
                    form = copy.deepcopy(data["table_row_map"]["form"])

                    with patch("weko_itemtypes_ui.admin.fix_json_schema",return_value=schema):
                        with patch("weko_itemtypes_ui.admin.update_text_and_textarea",return_value=(schema,form)):
                            # schema invalid, raise ValueError
                            with patch("weko_itemtypes_ui.admin.update_required_schema_not_exist_in_form",return_value={}):
                                res = client.post(url,json=data,headers={"Content-Type":"application/json"})
                                assert res.status_code == 400
                                result = json.loads(res.data)
                                assert result["msg"] == "Failed to register Item type. Schema is in wrong format."

                    flow_define = FlowDefine(id=2,flow_id=uuid.uuid4(),
                                        flow_name='Registration Flow',
                                        flow_user=1)
                    with db.session.begin_nested():
                        db.session.add(flow_define)
                    db.session.commit()
                    workflow = WorkFlow(flows_id=uuid.uuid4(),
                                    flows_name='test workflow01',
                                    itemtype_id=2,
                                    index_tree_id=None,
                                    flow_id=flow_define.id,
                                    is_deleted=False,
                                    open_restricted=False,
                                    location_id=None,
                                    is_gakuninrdm=False)
                    with db.session.begin_nested():
                        db.session.add(workflow)
                    db.session.commit()

                with patch("weko_workflow.utils.get_cache_data", return_value=True):
                    # get_cache_data is True
                    url = url_for("itemtypesregister.register",item_type_id=0)
                    res = client.post(url,json=data,headers={"Content-Type":"application/json"})
                    result = json.loads(res.data)
                    assert res.status_code == 400
                    assert result["msg"] == "Item type cannot be updated because import is in progress."

                render = item_type[1]["item_type"].render
                schema = copy.deepcopy(item_type[1]["item_type"].schema)
                data = {
                        "table_row_map":{
                            # "schema":{"object":"test schema"},
                            "schema": schema,
                            "form": item_type[1]["item_type"].form,
                            "name":"new item type name"
                        },
                        "meta_list":render["meta_list"],
                    }

                # success
                with patch("weko_workflow.utils.get_cache_data", return_value=False):
                    url = url_for("itemtypesregister.register",item_type_id=item_type[1]["item_type"].id)
                    with patch("weko_itemtypes_ui.admin.update_required_schema_not_exist_in_form",return_value=schema):
                        res = client.post(url,json=data,headers={"Content-Type":"application/json"})
                        result = json.loads(res.data)
                        assert result["msg"] == "Successfuly registered Item type."
                        assert result["redirect_url"] == "/admin/itemtypes/2"

#     def restore_itemtype(self, item_type_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_restore_itemtype -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_restore_itemtype(self,client,db,admin_view,users,item_type):
        login_user_via_session(client=client,email=users[0]["email"])
        url = url_for("itemtypesregister.restore_itemtype")

        res = client.post(url)
        result = json.loads(res.data)
        assert result["code"] == -1
        assert result["msg"] == 'An error has occurred.'

        url = url_for("itemtypesregister.restore_itemtype",item_type_id=1)
        res = client.post(url)
        result = json.loads(res.data)
        assert result["code"] == -1
        assert result["msg"] == 'An error has occurred.'

        item_type1 = item_type[0]["item_type"]
        item_type1.is_deleted=True
        db.session.merge(item_type1)
        db.session.commit()

        url = url_for("itemtypesregister.restore_itemtype",item_type_id=1)
        res = client.post(url)
        result = json.loads(res.data)
        assert result["code"] == 0
        assert result["msg"] == 'Restored Item type successfully.'

        item_type1 = item_type[0]["item_type"]
        item_type1.is_deleted=True
        db.session.merge(item_type1)
        db.session.commit()
        with patch("weko_itemtypes_ui.admin.ItemTypeNames.restore",side_effect=BaseException):
            res = client.post(url)
            result = json.loads(res.data)
            assert result["code"] == -1
            assert result["msg"] == 'Failed to restore Item type.'

#     def get_property_list(self, property_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_get_property_list -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_get_property_list(self,client,admin_view,db,itemtype_props,admin_settings,users):
        login_user_via_session(client=client,email=users[0]["email"])
        url = url_for("itemtypesregister.get_property_list")
        billing_permission = BillingPermission(user_id=1,is_active=True)
        db.session.add(billing_permission)
        db.session.commit()

        res = client.get(url,query_string={"lang":"en"})
        result = json.loads(res.data)
        test = {
            "system":{"2":{"name":"S_test2","schema":{},"form":{},"forms":{},"sort":None,"is_file":False}},
            "1":{"name":"test_name_en","schema":{"properties":{"filename":{"items":["test_file"]}}},"form":{"title_i18n":{"en":"test_name_en"}},"forms":{},"sort":None,"is_file":True},
            "3":{"name":"test3_exist_billing_file_prop","schema":{"billing_file_prop":True},"form":{},"forms":{},"sort":None,"is_file":False},
            "4":{"name":"test4_exist_system_prop","schema":{"system_prop":True},"form":{},"forms":{},"sort":None,"is_file":False},
            "defaults":{'1': {'name': 'Text Field', 'value': 'text'},'2': {'name': 'Text Area', 'value': 'textarea'},'3': {'name': 'Check Box', 'value': 'checkboxes'},'4': {'name': 'Radio Button', 'value': 'radios'},'5': {'name': 'List Box', 'value': 'select'},'6': {'name': 'Date', 'value': 'datetime'}},
        }
        assert result == test

        # settings.show_flag is false,billing_perm.is_active is false
        billing_permission.is_active=False
        db.session.merge(billing_permission)
        default_properties = admin_settings["default_properties"]
        default_properties.settings = {"show_flag": False}
        db.session.merge(default_properties)
        db.session.commit()
        res = client.get(url,query_string={"lang":"en"})
        result = json.loads(res.data)
        test = {
            "system":{"2":{"name":"S_test2","schema":{},"form":{},"forms":{},"sort":None,"is_file":False}},
            "1":{"name":"test_name_en","schema":{"properties":{"filename":{"items":["test_file"]}}},"form":{"title_i18n":{"en":"test_name_en"}},"forms":{},"sort":None,"is_file":True},
            "4":{"name":"test4_exist_system_prop","schema":{"system_prop":True},"form":{},"forms":{},"sort":None,"is_file":False},
            "defaults":{"0":{"name":"Date (Type-less）","value":"datetime"}}
        }
        assert result == test
        # adminsetting is None
        patch("weko_itemtypes_ui.admin.AdminSettings.get",return_value=None)
        res = client.get(url,query_string={"lang":"en"})
        result = json.loads(res.data)
        test = {
            "system":{"2":{"name":"S_test2","schema":{},"form":{},"forms":{},"sort":None,"is_file":False}},
            "1":{"name":"test_name_en","schema":{"properties":{"filename":{"items":["test_file"]}}},"form":{"title_i18n":{"en":"test_name_en"}},"forms":{},"sort":None,"is_file":True},
            "4":{"name":"test4_exist_system_prop","schema":{"system_prop":True},"form":{},"forms":{},"sort":None,"is_file":False},
            "defaults":{'1': {'name': 'Text Field', 'value': 'text'},'2': {'name': 'Text Area', 'value': 'textarea'},'3': {'name': 'Check Box', 'value': 'checkboxes'},'4': {'name': 'Radio Button', 'value': 'radios'},'5': {'name': 'List Box', 'value': 'select'},'6': {'name': 'Date', 'value': 'datetime'}},
        }
        assert result == test
        #
        current_app.config.update(
            WEKO_ITEMTYPES_UI_SHOW_DEFAULT_PROPERTIES=False
        )
        res = client.get(url,query_string={"lang":"en"})
        result = json.loads(res.data)
        test = {
            "system":{"2":{"name":"S_test2","schema":{},"form":{},"forms":{},"sort":None,"is_file":False}},
            "1":{"name":"test_name_en","schema":{"properties":{"filename":{"items":["test_file"]}}},"form":{"title_i18n":{"en":"test_name_en"}},"forms":{},"sort":None,"is_file":True},
            "4":{"name":"test4_exist_system_prop","schema":{"system_prop":True},"form":{},"forms":{},"sort":None,"is_file":False},
            "defaults":{"0":{"name":"Date (Type-less）","value":"datetime"}}
        }
        assert result == test

# TODO テスト対象のコードを変えたらテストがパスしたが本当にそれで問題ないのか確認すること。
#     def export(self,item_type_id):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_export -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_export(self,client,db,admin_view,users,item_type,itemtype_props):
        login_user_via_session(client=client,email=users[0]["email"])
        item_type1 = item_type[0]["item_type"]
        item_type1.harvesting_type = False
        db.session.merge(item_type1)
        db.session.commit()
        # not exist itemtype
        url = url_for("itemtypesregister.export",item_type_id=100)
        with patch("weko_itemtypes_ui.admin.ItemTypeMetaDataView.render",return_value=make_response()) as mock_render:
            res = client.get(url)
            mock_render.assert_called_with("weko_itemtypes_ui/admin/error.html")

            url = url_for("itemtypesregister.export",item_type_id=1)
            with patch("weko_itemtypes_ui.admin.send_file",return_value=make_response()) as mock_send:
                class MockZip:
                    def __init__(self, fp, mode, compression):
                        self.fp=fp
                    def writestr(self,filename,data):
                        self.fp.data[filename]=data
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc_value, traceback):
                        pass
                class MockBytesIO():
                    def __init__(self):
                        self.data = {}
                    def seek(self, flg):
                        pass

                with patch("weko_itemtypes_ui.admin.io.BytesIO",side_effect=MockBytesIO), \
                    patch("weko_itemtypes_ui.admin.ZipFile",side_effect=MockZip):
                    res = client.get(url)
                    fp, kwargs = mock_send.call_args
                    assert "ItemType.json" in fp[0].data
                    assert "ItemTypeName.json" in fp[0].data
                    assert "ItemTypeMapping.json" in fp[0].data
                    assert "ItemTypeProperty.json" in fp[0].data

#     def item_type_import(self):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMetaDataView::test_item_type_import -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
# TODO:zipファイルを扱う方法の調査
    def test_item_type_import(self,client,admin_view,users,item_type):
        login_user_via_session(client=client,email=users[0]["email"])
        url = url_for("itemtypesregister.item_type_import")
        file = FileStorage(filename="",stream=None)
        # not exist item_type_name
        res = client.post(url,data={"item_type_name":"","file":(file,"")},content_type="multipart/form-data")

        assert json.loads(res.data)["msg"] == 'No item type name Error'


        file = FileStorage(filename='test', stream=BytesIO(b'test'))
        res = client.post(url,data={"item_type_name":"テストアイテムタイプ1","file":file},
                          content_type="multipart/form-data")

# class ItemTypeSchema(SQLAlchemyAutoSchema):
#     class Meta:
# class ItemTypeNameSchema(SQLAlchemyAutoSchema):
#     class Meta:
# class ItemTypeMappingSchema(SQLAlchemyAutoSchema):
#     class Meta:
# class ItemTypePropertySchema(SQLAlchemyAutoSchema):
#     class Meta:
# class ItemTypePropertiesView(BaseView):
class TestItemTypePropertiesView():
#     def index(self, property_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_index_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,False),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_index_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesproperties.index")
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)

# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_index(self,client,db,admin_view,users,itemtype_props):
        login_user_via_session(client,email=users[0]["email"])
        billing_permission = BillingPermission(user_id=1,is_active=False)
        db.session.add(billing_permission)
        db.session.commit()

        url = url_for("itemtypesproperties.index")
        test_props = itemtype_props.copy()
        test_props.pop(3)
        test_props.pop(2)
        with patch("weko_itemtypes_ui.admin.ItemTypePropertiesView.render",return_value=make_response()) as mock_render:
            res = client.get(url)
            mock_render.assert_called_with(
                'weko_itemtypes_ui/admin/create_property.html',
                lists=test_props,
                lang_code="en"
            )

        billing_permission.is_active=True
        db.session.merge(billing_permission)
        db.session.commit()
        test_props=itemtype_props.copy()
        test_props.pop(3)

        with patch("weko_itemtypes_ui.admin.ItemTypePropertiesView.render",return_value=make_response()) as mock_render:
            res = client.get(url)
            mock_render.assert_called_with(
                'weko_itemtypes_ui/admin/create_property.html',
                lists=test_props,
                lang_code="en"
            )
#     def get_property(self, property_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_get_property -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,False),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_get_property_acl(self,client,admin_view,users,itemtype_props,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesproperties.get_property",property_id=1)
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_get_property -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_get_property(self,client,admin_view,users,itemtype_props):
        login_user_via_session(client,email=users[0]["email"])
        url = url_for("itemtypesproperties.get_property",property_id=1)
        res = client.get(url)
        assert res.status_code == 200
        result = json.loads(res.data)
        assert result["id"] == 1
        assert result["name"] == "test1"
        assert result["schema"] == {"properties":{"filename":{"items":["test_file"]}}}
        assert result["form"] == {"title_i18n":{"en":"test_name_en"}}
        assert result["forms"] == {}

#     def custom_property_new(self, property_id=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_custom_property_new -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,False),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_custom_property_new_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesproperties.custom_property_new")
        res = client.post(url,json={})
        assert_statuscode_with_role(res,is_permission)
        url = url_for("itemtypesproperties.custom_property_new",property_id=1)
        res = client.post(url,json={})
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypePropertiesView::test_custom_property_new -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_custom_property_new(self,client,admin_view,db,users):
        login_user_via_session(client,email=users[0]["email"])
        patch("weko_records.api.before_record_insert.send")
        patch("weko_records.api.after_record_insert.send")
        url = url_for("itemtypesproperties.custom_property_new")
        data = {
            "name":"new_prop",
            "schema":{"key_schema":"value_schema"},
            "form1":{"key_form1":"value_form1"},
            "form2":{"key_form2":"value_form2"}
        }
        res = client.post(url,json=data,headers={"Content-Type":"application/json"})
        assert res.status_code == 200
        assert json.loads(res.data)["msg"] == "Saved property successfully."
        result = obj = ItemTypeProperty.query.filter_by(id=1,
                                                       delflg=False).first()
        assert result.name == "new_prop"
        assert result.schema == {"key_schema":"value_schema"}

        # raise Exception
        with patch("weko_itemtypes_ui.admin.ItemTypeProps.create",side_effect=Exception):
            res = client.post(url,json=data,headers={"Content-Type":"application/json"})
            assert res.status_code == 200
            assert json.loads(res.data)["msg"] == 'Failed to save property.'

        # header is not application/json
        data = "test_data"
        res = client.post(url,headers={"Content-Type":"text/plain"})
        assert res.status_code ==200
        assert json.loads(res.data)["msg"] == "Header Error"
# class ItemTypeMappingView(BaseView):
class TestItemTypeMappingView:
#     def index(self, ItemTypeID=0):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_index_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_index_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesmapping.index")
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_index(self,app,client,admin_view,users,item_type,oaiserver_schema):
        login_user_via_session(client,email=users[0]["email"])
        login(app,client,obj=users[0]["obj"])
        url = url_for("itemtypesmapping.index")
        # not exist itemtypes
        with patch("weko_itemtypes_ui.admin.ItemTypes.get_latest",return_value=[]):
            with patch("weko_itemtypes_ui.admin.ItemTypeMappingView.render",return_value=make_response()) as mock_render:
                res = client.get(url)
                mock_render.assert_called_with("weko_itemtypes_ui/admin/error.html")

        # item_type is None
        with patch("weko_itemtypes_ui.admin.redirect",return_value=make_response()) as mock_render:
            res = client.get(url)
            mock_render.assert_called_with(
                "/admin/itemtypes/mapping/1"
            )

        url = url_for("itemtypesmapping.index",ItemTypeID=7)
        with patch("weko_itemtypes_ui.admin.ItemTypeMappingView.render",return_value=make_response()) as mock_render:
            with patch("weko_itemtypes_ui.admin.remove_xsd_prefix",return_value="called remove_xsd_prefix"):
                res = client.get(url,headers={"Accept-Language":"ja"})
                mock_render.assert_called_with(
                    "weko_itemtypes_ui/admin/create_mapping.html",
                    lists=[data["item_type_name"] for data in item_type],
                    hide_mapping_prop={},
                    mapping_name="jpcoar_mapping",
                    hide_itemtype_prop={"pubdate": {"type": "string","title": "PubDate","format": "datetime"},"test_not_form":{"title":"test_not_form_title"},"test_key1":{"title":"test_key1_no_title"},"test_key2":{"title":"test_key2_no_title"},"test_key3":{"title":"test_key3_no_title"},"test_key4":{"title":"test_key4_no_title"},"test_key5":{"title":"test_key5_no_title"},"test_key6":{"title":"test_key6_no_title"},"test_key7":{"title":"test_key7_no_title"},"test_key8":{"title":"test_key8_no_title"},"test_key9":{"title":"test_key9_no_title"},"test1_subkey1":{"title":"test1_subkey1_no_title"},"test2_subkey1":{"title":"test2_subkey1_no_title"},"test3_subkey1":{"title":"test3_subkey1_no_title"},"test4_subkey1":{"title":"test4_subkey1_no_title"},"test5_subkey1":{"title":"test5_subkey1_no_title"}},
                    jpcoar_prop_lists="called remove_xsd_prefix",
                    meta_system={
                        "system_identifier_doi":{
                            "title_i18n":{"en":"system_identifier_doi_en"},
                            "title":"system_identifier_doi_en"
                        },
                        "system_identifier_hdl":{
                            "title_i18n":{
                                "en":"system_identifier_hdl_en",
                                "ja":"system_identifier_hdl_ja"},
                            "title":"system_identifier_hdl_ja"
                        }
                    },
                    itemtype_list=[("pubdate","PubDate"),("test_key1","test1_ja"),("test_key2","test_key2_no_title"),("test_key3","test_key3_no_title"),("test_key4","test_key4_title"),("test_key5","test_key5_title"),("test_key6","test_key6_ja"),("test_key7","test_key7_no_title"),("test_key8","test_key8_no_title"),("test_key9","test_key9_title"),("test1_subkey1","test1_subkey1_title"),("test2_subkey1","test2_subkey1_no_title"),("test3_subkey1","test3_subkey1_no_title"),("test4_subkey1","test4.sub1.ja"),("test5_subkey1","test5.sub.title"),("test_not_form","test_not_form_title")],
                    id=7,
                    is_system_admin=True,
                    lang_code="en"
                )


#     def mapping_register(self):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_mapping_register_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_mapping_register_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesmapping.mapping_register")
        res = client.post(url,data="test",headers={"Content-Type":"text/plain"})
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_mapping_register -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_mapping_register(self,client,admin_view,users,item_type):
        with patch("weko_records.api.before_record_insert.send"):
            with patch("weko_records.api.after_record_insert.send"):
                login_user_via_session(client,email=users[0]["email"])
                url = url_for("itemtypesmapping.mapping_register")
                # header is not application/json
                res = client.post(url,data="test",headers={"Content-Type":"text/plain"})
                assert res.status_code == 200
                assert json.loads(res.data)["msg"] == "Header Error"

                data = {
                    "item_type_id":1,
                    "mapping":{"key":"test_mapping"}
                }
                # check_duplicate_mapping is not
                with patch("weko_itemtypes_ui.admin.check_duplicate_mapping",return_value=["item1","item2"]):
                    res = client.post(url,json=data)
                    assert res.status_code == 200
                    result = json.loads(res.data)
                    assert result["duplicate"] == True
                    assert result["err_items"] == ["item1","item2"]
                    assert result["msg"] == "Duplicate mapping as below:"

                with patch("weko_itemtypes_ui.admin.check_duplicate_mapping",return_value=[]):
                    # nomal
                    res = client.post(url,json=data)
                    assert res.status_code==200
                    assert json.loads(res.data)["msg"] == 'Successfully saved new mapping.'
                    assert  Mapping.get_record(1) == {"key":"test_mapping"}

                    # raise Exception
                    with patch("weko_itemtypes_ui.admin.Mapping.create",side_effect=BaseException):
                        res = client.post(url,json=data)
                        assert json.loads(res.data)["msg"] == "Unexpected error occurred."


#     def schema_list(self, SchemaName=None):
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_schema_list -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize("index,is_permission",[
        (0,True),
        (1,True),
        (2,False),
        (3,False),
        (4,False),
        (5,False),
        (7,False)
    ])
    def test_schema_list_acl(self,client,admin_view,users,index,is_permission):
        login_user_via_session(client,email=users[index]["email"])
        url = url_for("itemtypesmapping.schema_list",SchemaName="not_exist_oai")
        res = client.get(url)
        assert_statuscode_with_role(res,is_permission)
# .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeMappingView::test_schema_list -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_schema_list(self,client,admin_view,users,oaiserver_schema):
        login_user_via_session(client,email=users[0]["email"])
        #test = {"oai_dc_mapping":{"dc:title": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:creator": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:subject": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:description": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:publisher": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:contributor": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:date": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:type": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:format": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:identifier": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:source": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:language": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:relation": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:coverage": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}, "dc:rights": {"type": {"minOccurs": 1, "maxOccurs": 1, "attributes": [{"ref": "xml:lang", "name": "xml:lang", "use": "optional"}]}}}}
        test = {'oai_dc_mapping': {'contributor': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'coverage': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'creator': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'date': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'description': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'format': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'identifier': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'language': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'publisher': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'relation': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'rights': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'source': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'subject': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'title': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}, 'type': {'type': {'attributes': [{'name': 'xml:lang', 'ref': 'xml:lang', 'use': 'optional'}], 'maxOccurs': 1, 'minOccurs': 1}}}}
        url = url_for("itemtypesmapping.schema_list")
        # not exist SchemaName
        res = client.get(url)
        assert res.status_code == 200
        assert json.loads(res.data) == test

        # exist Schema
        url = url_for("itemtypesmapping.schema_list",SchemaName="oai_dc_mapping")
        res = client.get(url)
        assert res.status_code == 200
        assert json.loads(res.data) == test
        # not exist Schema
        url = url_for("itemtypesmapping.schema_list",SchemaName="not_exist_oai")
        res = client.get(url)
        assert res.status_code == 200
        assert json.loads(res.data) == {}


class TestItemTypeRocrateMappingView:
    # .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeRocrateMappingView::test_index_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize('index, is_admin', [
        (0, True),
        (1, True),
        (2, False),
        (3, False),
        (4, False),
        (5, False),
        (7, False)
    ])
    def test_index_acl(self, client, admin_view, users, index, is_admin):
        login_user_via_session(client, email=users[index]['email'])
        url = url_for('itemtypesrocratemapping.index')
        res = client.get(url)
        assert_statuscode_with_role(res, is_admin)

    # .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeRocrateMappingView::test_index -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_index(self, client, admin_view, item_type, users):
        login_user_via_session(client=client, email=users[0]['email'])

        # item_type_id is none : redirect first item type
        url = url_for('itemtypesrocratemapping.index')
        res = client.get(url)
        assert res.status_code == 302
        # assert res.headers['Location'] == 'http://test_server/admin/itemtypes/rocrate_mapping/1'
        assert res.headers['Location'] == '/admin/itemtypes/rocrate_mapping/1'

        # item_type_id is not exist : redirect first item type
        url100 = url_for('itemtypesrocratemapping.index', item_type_id=100)
        res = client.get(url100)
        assert res.status_code == 302
        # assert res.headers['Location'] == 'http://test_server/admin/itemtypes/rocrate_mapping/1'
        assert res.headers['Location'] == '/admin/itemtypes/rocrate_mapping/1'

        # item_type_id is normal : 200
        url1 = url_for('itemtypesrocratemapping.index', item_type_id=1)
        res = client.get(url1)
        assert res.status_code == 200

        # Item type table has no record : render error screen
        with patch('weko_records.api.ItemTypes.get_latest', return_value=[]):
            with patch('weko_itemtypes_ui.admin.ItemTypeRocrateMappingView.render', return_value=make_response()) as mock_render:
                url1 = url_for('itemtypesrocratemapping.index', item_type_id=1)
                res = client.get(url1)
                assert res.status_code == 200
                assert mock_render.call_args[0][0] == current_app.config['WEKO_ITEMTYPES_UI_ADMIN_ERROR_TEMPLATE']

        # Unexpected error : 500
        with patch('weko_records.api.ItemTypes.get_latest', side_effect=Exception('Unexpected error')):
            url1 = url_for('itemtypesrocratemapping.index', item_type_id=1)
            res = client.get(url1)
            assert res.status_code == 500

    # .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeRocrateMappingView::test_register_acl -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    @pytest.mark.parametrize('index, is_admin', [
        (0, True),
        (1, True),
        (2, False),
        (3, False),
        (4, False),
        (5, False),
        (7, False)
    ])
    def test_register_acl(self, client, admin_view, users, index, is_admin):
        login_user_via_session(client, email=users[index]['email'])
        url = url_for('itemtypesrocratemapping.register')
        data = {}
        res = client.post(url, json=data)
        assert_statuscode_with_role(res, is_admin)

    # .tox/c1/bin/pytest --cov=weko_itemtypes_ui tests/test_admin.py::TestItemTypeRocrateMappingView::test_register -vv -s --cov-branch --cov-report=term --basetemp=/code/modules/weko-itemtypes-ui/.tox/c1/tmp
    def test_register(self, client, admin_view, users, rocrate_mapping):
        login_user_via_session(client, email=users[0]['email'])
        url = url_for('itemtypesrocratemapping.register')

        # Create mapping
        data = {'item_type_id': 1, 'mapping': {'key1': 'new_value1'}}
        res = client.post(url, json=data)
        assert res.status_code == 200
        record = RocrateMapping.query.filter_by(item_type_id=1).one_or_none()
        assert record.mapping.get('key1') == 'new_value1'

        # Update mapping
        data = {'item_type_id': 2, 'mapping': {'key2': 'new_value2'}}
        res = client.post(url, json=data)
        assert res.status_code == 200
        record = RocrateMapping.query.filter_by(item_type_id=2).one_or_none()
        assert record.mapping.get('key2') == 'new_value2'

        # Content type is not json : 400
        data = 'text'
        headers = {'Content-Type': 'text/plain'}
        res = client.post(url, data=data, headers=headers)
        assert res.status_code == 400

        # Failed to register db : 500
        data = {}
        res = client.post(url, json=data)
        assert res.status_code == 500
