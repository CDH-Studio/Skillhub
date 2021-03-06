import appSaga from "./app.sagas";
import authSaga from "./auth.sagas";
import profilesSaga from "./profiles.sagas";
import projectChangeRecordsSaga from "./projectChangeRecords.sagas";
import projectsSaga from "./projects.sagas";
import skillsSaga from "./skills.sagas";
import UsersSaga from "./users.sagas";

const sagas = [appSaga, authSaga, profilesSaga, projectChangeRecordsSaga, projectsSaga, skillsSaga, UsersSaga];

const registerSagas = (middleware) => sagas.forEach((saga) => middleware.run(saga));

export default registerSagas;
