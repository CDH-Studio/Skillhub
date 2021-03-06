import React, {useCallback} from "react";
import {useInput} from "utils/hooks";
import {Project} from "utils/models";
import {DetailsDialog, RoleInputDialog} from "components/";
import {IconButton, Paper} from "@material-ui/core";
import {Add, Create} from "@material-ui/icons";
import classNames from "classnames";
import connect from "./connect.js";
import "./ProjectInfo.scss";

const ProjectInfo = ({
    clearPatchError, addProjectError, patchProjectError, project, clearAddError,
    onPatchProject, onAddProject, open, setDialogState, profile, roleInputDialogOpen
}) => {
    const openDialog = () => {
        setDialogState("projectInfo", true);
    };

    const closeDialog = () => {
        if (patchProjectError) {
            clearPatchError();
        }
        setDialogState("projectInfo", false);
    };

    const openRoleInputDialog = () => {
        setDialogState("roleInput", true);
    };

    const closeRoleInputDialog = () => {
        if (addProjectError) {
            clearAddError();
        }
        setDialogState("roleInput", false);
    };

    return (
        <>
            <ProjectInfoDialog
                closeDialog={closeDialog}
                error={patchProjectError}
                key={open ? project : patchProjectError}
                onSubmit={onPatchProject}
                open={open}
                project={project}
            />
            <RoleInputDialog
                closeDialog={closeRoleInputDialog}
                currentProject={project}
                dialogTitle="Add to my Profile"
                error={addProjectError}
                key={roleInputDialogOpen}
                open={roleInputDialogOpen}
                onSubmit={onAddProject}
                profile={profile}
            />
            <Paper className="project-details-card">
                <div className="project-info-card-active-section">
                    <ActiveBadge isActive={Project.isActive(project)} />
                </div>
                <div className="project-info-card-content-section">
                    <h3 className="project-info-card-name">{project.name}</h3>
                    <p className="project-info-card-description">{project.description}</p>
                </div>
                <div className="project-info-card-edit-section">
                    <IconButton className="project-info-card-edit-button" onClick={openDialog} color="primary">
                        <Create />
                    </IconButton>
                    <IconButton className="project-info-card-add-button" onClick={openRoleInputDialog} color="primary">
                        <Add />
                    </IconButton>
                </div>
            </Paper>
        </>
    );
};

const ProjectInfoDialog = ({closeDialog, error, open, onSubmit, project}) => {
    const formFieldData = {
        "nameInput": {
            ...useInput(project.name),
            id: "name",
            label: "Name",
            autoFocus: true
        },
        "descriptionInput": {
            ...useInput(project.description),
            id: "description",
            label: "Description",
            multiline: true
        },
    };

    const {value: name} = formFieldData.nameInput;
    const {value: description} = formFieldData.descriptionInput;

    const onSubmitClick = useCallback(() => onSubmit(
        project.id, name, description
    ), [
        project.id, name, description, onSubmit
    ]);

    const formFieldDataById = Object.values(formFieldData).reduce((acc, formField) => {
        acc[formField.id] = formField;
        return acc;
    }, {});

    /* Set the error property for incorrectly filled in fields */
    if (error && error.message === "Missing Data") {
        for (const invalidFieldIndex of Object.keys(error.data)) {
            formFieldDataById[invalidFieldIndex].error = true;
            formFieldDataById[invalidFieldIndex].helperText = error.data[invalidFieldIndex];
        }
    }
    return (
        <DetailsDialog
            closeDialog={closeDialog}
            dialogTitle="Edit Project Info"
            formFieldData={formFieldData}
            open={open}
            onSubmit={onSubmitClick}
        />
    );
};

const ActiveBadge = ({isActive = true}) => (
    <TextBadge
        className="active-badge"
        text={isActive ? "Active" : "Inactive"}
        isHighlighted={isActive}
    />
);

const TextBadge = ({className, text, isHighlighted = false}) => (
    <div
        className={classNames(
            "text-badge",
            {"text-badge--highlighted": isHighlighted},
            className
        )}
    >
        {text}
    </div>
);

export default connect(ProjectInfo);