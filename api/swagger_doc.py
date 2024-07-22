from sys import prefix
from .common.config import settings

dev_prefix = settings.dev_prefix

checkbox = """<input type="checkbox" checked>"""
uncheckbox = """<input type="checkbox" unchecked disabled>"""
description = f"""
The ChurchMan App is a Church Management Solution (ChMS) that helps Churches manage her members, groups, events, assets, communications and finances (tithes, offerings, donations, seeds etc).

# Modules

## 1. Church Administration (_in progress_)
This manages the Church Hierarchy, Head Church, Churches at different levels and Church Leads, Groups and Sub-Groups.
This has the folowing Sub-Modules and endpoints:

### 1.1 Herarchy Sub-Module
{checkbox} Get All Hierarchies &nbsp;
{checkbox} Get Hierarchy by Code &nbsp;
{checkbox} Activate Hierarchy by Code &nbsp;
{checkbox} Deactivate Hierarchy by Code &nbsp;
{checkbox} Update Hierarchy by Code &nbsp;
<hr>

### 1.2 Head Church Sub-Module
{checkbox} Create New Head Church &nbsp;
{checkbox} Get Head Church by Code &nbsp;
{checkbox} Update Head Church by Code &nbsp;
{checkbox} Activate Head Church by Code (Super Admin only) &nbsp;
{checkbox} Deactivate Head Church by Code (Super Admin only) &nbsp;
<hr>

### 1.3 Churches Sub-Module
{checkbox} Create New Church &nbsp;
{checkbox} Approved Church by Code &nbsp;
{checkbox} Get All Churches &nbsp;
{checkbox} Get Churches by Level &nbsp;
{checkbox} Get Church by Code &nbsp;
{checkbox} Update Church by Code &nbsp;
{checkbox} Activate Church by Code &nbsp;
{checkbox} Deactivate Church by Code &nbsp;
<hr>

### 1.4 Church Leads Sub-Module
{checkbox} Get Church Leads by Code &nbsp;
{checkbox} Unmap Church Leads by Code &nbsp;
{checkbox} Map Church Leads by Code &nbsp;
{checkbox} Get Churches by Lead Code &nbsp;
<hr>

### 1.5 Groups Sub-Module
{uncheckbox} Create New Group &nbsp;
{uncheckbox} Get All Groups &nbsp;
{uncheckbox} Get Group by Code &nbsp;
{uncheckbox} Get Group by Church Code &nbsp;
{uncheckbox} Get Groups by Level Code &nbsp;
{uncheckbox} Update Group by Code &nbsp;
{uncheckbox} Activate Group by Code &nbsp;
{uncheckbox} Deactivate Group by Code &nbsp;
<hr>
<br>

## 2. Members Management (_in progress_) 
This manages Members, Member Branch, Member Groups, Church Positions, Member Positions etc.

### 2.1 Members Sub-Module
{checkbox} Create New Member &nbsp;
{checkbox} Get All Members &nbsp;
{checkbox} Get Member by Code &nbsp;
{checkbox} Get Current User Member &nbsp;
{checkbox} Get Members by Church Code &nbsp;
{checkbox} Get Members by Level Code &nbsp;
{checkbox} Update Member by Code &nbsp;
{checkbox} Update Current User Member &nbsp;
{checkbox} Activate Member by Code &nbsp;
{checkbox} Deactivate Member by Code &nbsp;
<hr>
<br>

### 2.2 Member Positions Sub-Module
{uncheckbox} Create New Member Position &nbsp;
{uncheckbox} Get All Member Positions &nbsp;
{uncheckbox} Get Member Position by Code &nbsp;
{uncheckbox} Get Member Positions by Member Code &nbsp;
{uncheckbox} Update Member Position by Code &nbsp;
{uncheckbox} Activate Member Position by Code &nbsp;
{uncheckbox} Deactivate Member Position by Code &nbsp;
<hr>
<br>


## 3. User Management (_in progress_)
This managers users, user roles, user access to modules and submodules.

## 4. Asset Management (_not implemented_)
This manages assets, asset types, assets allocation and locations.

## 5. Event Management (_not implemented_)
This manages program events and events details.

## 6. Finance Management (_not implemented_)
This manages tithes, offerings, donations, seeds etc.

## 7. Communication Management (_not implemented_)
This manages all communication channels and messages.

<br>
"""

tags = {
    # AUTHENTICATION MODULE
    "auth": {
        "module": "Authentication (AUTH)",
        "submodule": "Authentication Sub-Module (AUTH)",
        "description": "Operations on User Authentications",
    },
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
    },
    "churches": {
        "module": "Church Administration (CHAD)",
        "submodule": "Churches Sub-Module (CHUR)",
        "description": "Operations on Churches",
    },
    "church_leads": {
        "module": "Church Administration (CHAD)",
        "submodule": "Church Leads Sub-Module (LEAD)",
        "description": "Operations on Church Leads",
    },
    # GROUPS MANAGEMENT MODULE
    "groups": {
        "module": "Groups Management (GRPM)",
        "submodule": "Groups Sub-Module (GRUP)",
        "description": "Operations on Groups",
    },
    "subgroups": {
        "module": "Groups Management (GRPM)",
        "submodule": "Sub Groups Sub-Module (SUBG)",
        "description": "Operations on Sub Groups",
    },
    # MEMBERSHIP MANAGEMENT MODULE
    "members": {
        "module": "Membership Management (MBSM)",
        "submodule": "Members Sub-Module (MBRS)",
        "description": "Operations on Members",
    },
    "member_branch": {
        "module": "Membership Management (MBSM)",
        "submodule": "Member Branch Sub-Module (MBRN)",
        "description": "Operations on Member's Branch",
    },
    "member_groups": {
        "module": "Membership Management (MBSM)",
        "submodule": "Member Groups Sub-Module (MGRP)",
        "description": "Operations on Member's Groups",
    },
    "member_position": {
        "module": "Membership Management (MBSM)",
        "submodule": "Member Positions Sub-Module (MBPO)",
        "description": "Operations on Member's Position",
    },
    # USER MANAGEMENT MODULE
    "users": {
        "module": "User Management (USRM)",
        "submodule": "Users Sub-Module (USAD)",
        "description": "Operations on Users",
    },
}

openapi_tags = [
    # Authentication Module
    {
        "name": f"{tags['auth']['module']}: {tags['auth']['submodule']}",
        "description": f"{tags['auth']['description']}",
    },
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
    },
    # Churches Sub Module
    {
        "name": f"{tags['churches']['module']}: {tags['churches']['submodule']}: Admin only",
        "description": f"{tags['churches']['description']}: Admins only",
    },
    {
        "name": f"{tags['churches']['module']}: {tags['churches']['submodule']}",
        "description": f"{tags['churches']['description']}",
    },
    # Church Leads Sub Module
    {
        "name": f"{tags['church_leads']['module']}: {tags['church_leads']['submodule']}: Admin only",
        "description": f"{tags['church_leads']['description']}: Admins only",
    },
    {
        "name": f"{tags['church_leads']['module']}: {tags['church_leads']['submodule']}",
        "description": f"{tags['church_leads']['description']}",
    },
    # GROUP MANAGEMENT MODULE
    # Group Sub Module
    {
        "name": f"{tags['groups']['module']}: {tags['groups']['submodule']}: Admin only",
        "description": f"{tags['groups']['description']}: Admins only",
    },
    {
        "name": f"{tags['groups']['module']}: {tags['groups']['submodule']}",
        "description": f"{tags['groups']['description']}",
    },
    # Sub Group Sub Module
    {
        "name": f"{tags['subgroups']['module']}: {tags['subgroups']['submodule']}: Admin only",
        "description": f"{tags['subgroups']['description']}: Admins only",
    },
    {
        "name": f"{tags['subgroups']['module']}: {tags['subgroups']['submodule']}",
        "description": f"{tags['subgroups']['description']}",
    },
    ## MEMBERSHIP MANAGEMENT MODULE
    # Members Sub Module
    {
        "name": f"{tags['members']['module']}: {tags['members']['submodule']}: Admin only",
        "description": f"{tags['members']['description']}: Admins only",
    },
    {
        "name": f"{tags['members']['module']}: {tags['members']['submodule']}",
        "description": f"{tags['members']['description']}",
    },
    # Member-Branch Sub Module
    {
        "name": f"{tags['member_branch']['module']}: {tags['member_branch']['submodule']}: Admin only",
        "description": f"{tags['member_branch']['description']}: Admins only",
    },
    {
        "name": f"{tags['member_branch']['module']}: {tags['member_branch']['submodule']}",
        "description": f"{tags['member_branch']['description']}",
    },
    ## USER MANAGEMENT MODULE
    # User Management Sub Module
    {
        "name": f"{tags['users']['module']}: {tags['users']['submodule']}: Admin only",
        "description": f"{tags['users']['description']}: Admins only",
    },
    {
        "name": f"{tags['users']['module']}: {tags['users']['submodule']}",
        "description": f"{tags['users']['description']}",
    },
]


def get_swagger_params(prefix):
    swagger_params = dict(
        title="ChurchMan App",
        summary="An all-in-one Church Management Solution.",
        description=description,
        version="0.0.1",
        contact={
            "name": "Gregory Ogbemudia",
            "url": "https://github.com/OSQUAREG",
            "email": "gregory.ogbemduia@gmail.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://spdx.org/licenses/MIT.html",
            "identifier": "MIT",
        },
        servers=[
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local server",
            },
            {
                "url": "https://development.churchman.com",
                "description": "Development server",
            },
            {
                "url": "https://test.churchman.com",
                "description": "Test server",
            },
            {
                "url": "https://staging.churchman.com",
                "description": "Staging server",
            },
            {
                "url": "https://api.churchman.com",
                "description": "Production server",
            },
        ],
        openapi_url=f"{prefix}/openapi.json",
        docs_url=f"{prefix}/docs",
        openapi_tags=openapi_tags,
        persistAuthorization=True,
    )
    return swagger_params
