export interface Activity {
  _id: string;
  user_id: string;
  activityId: number;
  activityName: string;
  startTimeLocal: string;
  startTimeGMT: string;
  activityType: string;
  distance: number;
  duration: number;
  elapsedDuration: number;
  movingDuration: number;
  elevationGain: number | null;
  elevationLoss: number | null;
  averageSpeed: number;
  maxSpeed: number;
  calories: number;
  bmrCalories: number;
  averageHR: number;
  maxHR: number;
  averageRunningCadenceInStepsPerMinute: number;
  maxRunningCadenceInStepsPerMinute: number;
  steps: number;
  avgPower: number;
  maxPower: number;
  normPower: number;
  avgVerticalOscillation: number;
  avgGroundContactTime: number;
  avgStrideLength: number;
  avgVerticalRatio: number;
  minElevation: number | null;
  maxElevation: number | null;
  maxDoubleCadence: number;
  summarizedDiveInfo: object | null;
  maxVerticalSpeed: number | null;
  locationName: string | null;
  moderateIntensityMinutes: number;
  vigorousIntensityMinutes: number;
  fastestSplit_1000: number | null;
  fastestSplit_1609: number | null;
  fastestSplit_5000: number | null;
  pr: boolean;
  manualActivity: boolean;
  workoutTemplate?: WorkoutTemplate;
  workoutData?: {
    workout_template_id: string;
    user_id: string;
    template_name: string;
    exercise_entries: {
      exercise_id: string | null;
      sets: number;
      weights: number[];
      reps: number[];
      failure: boolean[];
    }[];
  }
}


export interface CategorizedActivity {
  duration: number;
  distance: number;
  calories: number;
}

export interface ActivitiesByCategory {
  running: CategorizedActivity[];
  cycling: CategorizedActivity[];
  swimming: CategorizedActivity[];
  strength: CategorizedActivity[];
}

export type ActivitiesByDate = {
  [date: string]: ActivitiesByCategory;
};

export type MealsByDate = {
  [date: string]: ActivitiesByCategory;
};

export interface DailyIntake {
  day: string; total_carbs: number; total_fats: number; total_proteins: number, total_calories: number
}

export interface NutritionItem {
  _id: number;
  isCustom: boolean;
  name: string;
  weight: number;
  per100: NutritionData
  total_macros: NutritionData
}

export interface NutritionData {
  carbs: number;
  fats: number;
  proteins: number;
  sugars: number;
  calories: number;
}

export interface NutritionDB {
  carbs: number;
  fats: number;
  proteins: number;
  sugars: number;
  calories: number;
  _id: number;
  name: string;
}

export interface Meal {
  _id: string;
  user_id: string;
  name: string;
  selectedItems: NutritionItem[];
  created_at: string;
}

export interface Exercise {
  _id: string,
  title: string;
  desc: string;
  type: string;
  body_part: string;
  equipment: string;
  level: string;
}

export interface WorkoutTemplate {
  _id: string;
  user_id: string;
  name: string;
  selectedItems: ExerciseItem[];
}

export interface ExerciseItem {
  isCustom: boolean;
  exercise?: Exercise;
  sets: number
}

export interface ActivityDetailsData {
  activityId: number,
  activityTime: number[],
  metrics: Metric[]
}

export interface Metric {
  key: string,
  unit: string,
  values: number[]
}