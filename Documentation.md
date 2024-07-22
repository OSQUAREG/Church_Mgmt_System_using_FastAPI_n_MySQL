# ChurchMan - Church Management Solution (ChMS)

## Introduction

The ChurchMan App is a Church Management Solution (ChMS) that helps Churches manage her hierarchy, members, branches, groups, events, assets, communications and finances (tithes, offerings, donations, seeds etc).

## Modules, Sub-Modules and Endpoints

### Using OpenAPI tags and Route methods params as Modules, Sub-Modules and Endpoints inserted into the DB

1. Define or add new tags keys in the `ChMS\api\swagger_doc.py` file as seen in the sample below.

   ```
   tags = {
       # CHURCH ADMINISTRATION MODULE
       "hierarchy": {
           "module": "Church Administration (CHAD)",
           "submodule": "Hierarchy Sub-Module (HIER)",
           "description": "Operations on Church Hierarchies",
       },
       "head_church": {
           "module": "Church Administration (CHAD)",
           "submodule": "Head Church Sub-Module (HEAD)",
           "description": "Operations on the Head Church",
       }, ...
   }
   ```
2. Use the tags dictionary as seen below:

   ```
   openapi_tags = [
       # CHURCH ADMINISTRATION MODULE
       # Hierarchy Sub Module
       {
           "name": f"{tags['hierarchy']['module']}: {tags['hierarchy']['submodule']}",
           "description": f"{tags['hierarchy']['description']}",
       },
       # Head Church Sub Module
       {
           # "name": "Head Church Sub-Module Operations - Super Admin only",
           "name": f"{tags['head_church']['module']}: {tags['head_church']['submodule']}: Super Admin only",
           "description": f"{tags['head_church']['description']}: Super Admin only",
       },
       {
           "name": f"{tags['head_church']['module']}: {tags['head_church']['submodule']}",
           "description": f"{tags['head_church']['description']}",
       }, ...
   ]
   ```
3. Then pass the above openapi_tags list(dict) to the swagger param `openapi_tags` for the FastAPI class, as seen below:

   ```
   swagger_params = dict(
           title="ChurchMan App",
           ...,
           openapi_tags=openapi_tags,
       )
   ```
4. Import the tags into the various .py files containing the routes and use them as seen below:

   ```
   from fastapi import APIRouter
   from ...swagger_doc import tags

   hierarchy_router = APIRouter(
       prefix="/admin/hierarchy",
       tags=[f"{tags['hierarchy']['module']}: {tags['hierarchy']['submodule']}"],
   )

   church_router = APIRouter(
       prefix=f"/church",
       tags=[f"{tags['churches']['module']}: {tags['churches']['submodule']}"],
   )

   church_adm_router = APIRouter(
       prefix=f"/admin/church",
       tags=[f"{tags['churches']['module']}: {tags['churches']['submodule']}: Admin only"],
   )
   ```
5. Also define your route methods params as seen below.
   Note: The `name` param will be used as the Endpoint name and also transformed into the endpoint code, while the `description` param will be used as description in the tblEndpoints table.

   ```
   @hierarchy_router.get(
       "/",
       status_code=status.HTTP_200_OK,
       name="Get Hierarchies",
       summary="Get All Hierarchies",
       description="## Retrieve All Hierarchies",
       response_model=HierarchyResponse,
   )
   ```
6. The functions `def get_all_endpoints(app: FastAPI)` and `def insert_mod_sub_endpts_table(app: FastAPI)` in `ChMS\api\common\database.py` helps extract the Module, Sub-Module and Endpoints names and codes and insert them into the tblModules, tblSubModules and tblEndpoints tables respectively.
7. Each time there are modifications, on the API, this functions will truncate and re-insert into the tables.

## Module 1: Authentication & Authorization

### DB Tables

| Generic Schema Tables | Head Schema Tables |
| --------------------- | ------------------ |
| tblEndpoints          | tblRoles           |
| tblSubModules         | tblRoleAccess      |
| tblModules            | tblUsers           |
|                       | tblUserRole        |

### Strategy

In tblUserRole, a Role [`Role_Code`] (FK from tblRoles) is assigned to a User [`Usercode`] (FK from tblUsers) for a Church Level [`Level_Code`] (FK from tblChurchLevels) and for a Church [`Church_Code`] (FK from tblChurches).

In tblRoleAccess, a Role [`Role_Code`] (FK from tblRoles) is assigned Endpoints [Access_Code] (FK from tblEndpoints)

In tblEndpoints, an Endpoint [`Code`] gives access and access type (create, read, update, delete and approve/reject) to the connected SubModule [`SubModule_Code`] (FK from tblSubmodules), which in tblModules is in turn connected to a Module [`Module_Code`] (FK from tblModules) to the User to which the Role is assigned.

### Authentication Process/Steps

1. **Initial Authentication**: The User logs in using Usercode and Password, and a token is created. This uses the endpoint `AUTHENTICATE_USER`
2. **Re-Authentication**: The User selects a "Church Level" from a list of Church Levels mapped to his assigned Role(s).
   The endpoint `RE_AUTHENTICATE_USER` uses the token created in the initial authentication and the selected Church Level to create a new token that is then used to access specific Endpoints, SubModules and Modules according to the assigned Role for that Church Level.

### Authorization Implementation

At Re-Authentication, the `Level_Code` and `Church_Code` from tblUserRole for the `Level_Code` selected is stored in the new token and used to check if a user has access to certain Church Level or Church.

The Role (of the user at the selected level) determines where (submodule and module) and to what extent (endpoints) the user can perform at that church level and church selected.

### Routes/Endpoints

- [X] Authenticate User - AUTHENTICATE_USER
- [X] Re-Authenticate User - RE_AUTHENTICATE_USER
- [X] Read Current User - READ_CURRENT_USER
- [X] Read Current User Access - READ_CURRENT_USER_ACCESS
- [X] Read Current User Level - READ_CURRENT_USER_LEVEL

## Module 2: Church Administration

This manages the Church Hierarchy, Head Church, Church Levels and Church Leads, Groups and Sub-Groups.

### Hierarchy Sub-Module

This is used for operations on all Church Level operations.

#### DB Tables

| Generic Schema Tables | Head Schema Tables |
| --------------------- | ------------------ |
| tblHierarchy          | tblChurchLevels    |

#### Routes/Endpoints

- [X] Get Hierarchies - GET_HIERARCHIES
- [X] Get Hierarchy - GET_HIERARCHY
- [X] Activate Hierarchy - ACTIVATE_HIERARCHY
- [X] Deactivate Hierarchy - DEACTIVATE_HIERARCHY
- [X] Update Hierarchy - UPDATE_HIERARCHY

### Head Church Sub-Module

#### DB Tables

| Generic Schema Tables | Head Schema Tables |
| --------------------- | ------------------ |
| tblChurchHeads        | tblChurches        |

#### Routes/Endpoints

* [X] Create New Head Church - CREATE_NEW_HEAD_CHURCH
* [X] Get Head Church - GET_HEAD_CHURCH
* [X] Deactivate Head Church - DEACTIVATE_HEAD_CHURCH
* [X] Activate Head Church - ACTIVATE_HEAD_CHURCH
* [X] Update Head Church - UPDATE_HEAD_CHURCH

### Churches Sub-Module

#### DB Tables

| Head Schema Tables |
| ------------------ |
| tblChurches        |

#### Routes/Endpoints

- [ ] Create New Church - CREATE_NEW_CHURCH
- [ ] Get All Churches - GET_ALL_CHURCHES
- [ ] Get Church - GET_CHURCH
- [ ] Get Churches by Level - GET_CHURCHES_BY_LEVEL
- [ ] Approve Church - APPROVE_CHURCH
- [ ] Update Church - UPDATE_CHURCH
- [ ] Activate Church - ACTIVATE_CHURCH
- [ ] Deactivate Church - DEACTIVATE_CHURCH

### Church Leads Sub-Module

#### DB Tables

| Head Schema Tables |
| ------------------ |
| tblChurchLeads     |
| tblChurches        |

#### Routes/Endpoints

- [ ] Map Church Lead - MAP_CHURCH_LEAD
- [ ] Unmap Church Lead - UNMAP_CHURCH_LEAD
- [ ] Approve Church Lead - APPROVE_CHURCH_LEAD
- [ ] Get Church Lead - GET_CHURCH_LEAD
- [ ] Get Church Lead Hierarchy - GET_CHURCH_LEAD_HIERARCHY
- [ ] Get Branches by Church Lead - GET_BRANCHES_BY_CHURCH_LEAD
- [ ] Get Churches by Lead - GET_CHURCHES_BY_LEAD

## Module 3: Membership Management

This manages Members, Member Branch, Member Groups, Church Positions, Member Positions, Member Groups etc.

### Members Sub-Module

#### DB Tables

| Head Schema Tables |
| ------------------ |
| tblMembers         |
| tblMemberBranch    |

#### Routes/Endpoints

* [ ] Create New Member - CREATE_NEW_MEMBER
* [ ] Get All Members - GET_ALL_MEMBERS
* [ ] Get Member - GET_MEMBER
* [ ] Get Members by Church - GET_MEMBERS_BY_CHURCH
* [ ] Get Current User Member - GET_CURRENT_USER_MEMBER
* [ ] Activate Member - ACTIVATE_MEMBER
* [ ] Deactivate Member - DEACTIVATE_MEMBER
* [ ] Update Member - UPDATE_MEMBER
* [ ] Update Current User Member - UPDATE_CURRENT_USER_MEMBER
* [ ] Promote Member to Clergy - PROMOTE_MEMBER_TO_CLERGY
* [ ] Demote Member from Clergy - DEMOTE_MEMBER_FROM_CLERGY

### Member Branch Sub-Module

#### DB Tables

| Head Schema Tables |
| ------------------ |
| tblMemberBranch    |
| tblMembers         |
| tblChurches        |

#### Routes/Endpoints

* [ ] Join Member To Church - JOIN_MEMBER_TO_CHURCH
* [ ] Exit Member From Church - EXIT_MEMBER_FROM_CHURCH
* [ ] Exit Member From All Churches - EXIT_MEMBER_FROM_ALL_CHURCHES
* [ ] Get Specific Member-Branch - GET_SPECIFIC_MEMBER_BRANCH
* [ ] Get Member Current Branch - GET_MEMBER_CURRENT_BRANCH
* [ ] Get All Member-Branches by Member - GET_ALL_MEMBER_BRANCHES_BY_MEMBER
* [ ] Get Member Church Hierarchy - GET_MEMBER_CHURCH_HIERARCHY
* [ ] Update Member-Branch Reason - UPDATE_MEMBER_BRANCH_REASON

## Module 4: User Administration
