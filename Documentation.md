# Church Management System (ChMS) Modules

## Module 1: Admin

### Head Church Admin

#### Service methods

- [X] Create Head Church
- [X] Get All Head Church
- [X] Activate Head Church by Code
- [X] Deactivate Head Church by Code
- [X] Delete Head Church by Code

#### Route functions

- [ ] Create New Head Church
- [ ] Get All Head Churches
- [ ] Activate Head Church by Code
- [ ] Deactivate Head Church by Code
- [ ] Delete Head Church by Code

## Module 2: Hierarchy Management

### Hierarchy

#### Schema models

* [X] **Hierarchy** – the basic hierarchy schema model used for creating hierarchy.
* [X] **HierarchyResponse** – used in the validation and returning Hierarchy fetched from the DB.

#### Service methods

**HierarchyService class**

- [X] **Get All Hierarchies** - returns all hierarchy related to user's head church with their status.
- [X] **Get Hierarchy by Code** - returns an hierarcy level related to user's head church with its status.
- [X] **Activate Hierarchy by Code** - returns activated hierarchy of user's head church.
- [X] **Deactivate Hierarchy by Code** - returns deactivated hierarchy of user's head church.

#### Route functions

- [X] **Get All Hierarchies** - gets all the hierarchies related to user's Head Church with their status
- [X] **Get Hierarchy by Code** - gets only one hierarchy by provided code
- [X] **Activate Hierarchy by Code** - activates a specified hierarchy in a user's Head Church
- [X] **Deactivate Hierarchy by Code** - deactivates a specified hierarchy in a user's Head Church
- [ ] Update Hierarchy by Code - updates the church level name or code.

### Head Church

#### Schema models

* [X] HeadChurch
* [X] HeadChurchResponse
* [X] HeadChurchUpdate

#### Service methods

* [X] Get Head Church by Code
* [X] Update Head Church by Code

#### Route functions

* [X] Get Head Church by Code
* [X] Update Head Church by Code

### Province

#### Schema models

* [X] Province
* [X] ProvinceResponse
* [X] ProvinceUpdate

#### Service methods

- [X] Create New Province
- [ ] Get All Provinces
- [ ] Get Province by Code
- [ ] Update Province by Code
- [ ] Activate Province by code
- [ ] Deactivate Province by Code

#### Route functions

- [ ] Create New Province
- [ ] Get All Provinces
- [ ] Get Province by Code
- [ ] Update Province by Code
- [ ] Activate Province by code
- [ ] Deactivate Province by Code

### Zone

#### Schema models

* [ ] Zone
* [ ] ZoneResponse
* [ ] ZoneUpdate

#### Service methods

- [ ] Create New Zone
- [ ] Get All Zones
- [ ] Get Zone by Code
- [ ] Update Zone by Code
- [ ] Activate Zone by code
- [ ] Deactivate Zone by Code

#### Route functions

- [ ] Create New Zone
- [ ] Get All Zones
- [ ] Get Zone by Code
- [ ] Update Zone by Code
- [ ] Activate Zone by code
- [ ] Deactivate Zone by Code

### Area

#### Schema models

* [ ] Area
* [ ] AreaResponse
* [ ] AreaUpdate

#### Service methods

- [ ] Create New Area
- [ ] Get All Areas
- [ ] Get Area by Code
- [ ] Update Area by Code
- [ ] Activate Area by code
- [ ] Deactivate Area by Code

#### Route functions

- [ ] Create New Area
- [ ] Get All Areas
- [ ] Get Area by Code
- [ ] Update Area by Code
- [ ] Activate Area by code
- [ ] Deactivate Area by Code

### Branch

#### Schema models

* [ ] Branch
* [ ] BranchResponse
* [ ] BranchUpdate

#### Service methods

- [ ] Create New Branch
- [ ] Get All Branches
- [ ] Get Branch by Code
- [ ] Update Branch by Code
- [ ] Activate Branch by code
- [ ] Deactivate Branch by Code

#### Route functions

- [ ] Create New Branch
- [ ] Get All Branches
- [ ] Get Branch by Code
- [ ] Update Branch by Code
- [ ] Activate Branch by code
- [ ] Deactivate Branch by Code
