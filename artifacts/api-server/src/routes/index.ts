import { Router, type IRouter } from "express";
import healthRouter from "./health";
import researchRouter from "./research";
import trainingRouter from "./training";
import evaluationsRouter from "./evaluations";
import inferenceRouter from "./inference";

const router: IRouter = Router();

router.use(healthRouter);
router.use(researchRouter);
router.use(trainingRouter);
router.use(evaluationsRouter);
router.use(inferenceRouter);

export default router;
