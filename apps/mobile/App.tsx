import React from "react";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";

import { AuthScreen } from "@src/screens/AuthScreen";
import { ProjectsScreen } from "@src/screens/ProjectsScreen";
import { StageListScreen } from "@src/screens/StageListScreen";
import { StageDetailScreen } from "@src/screens/StageDetailScreen";

export type RootStackParamList = {
  Auth: undefined;
  Projects: undefined;
  StageList: { projectId: string };
  StageDetail: { projectId: string; stageId: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: "#F5F5F5"
  }
};

export default function App() {
  return (
    <NavigationContainer theme={theme}>
      <StatusBar style="dark" />
      <Stack.Navigator
        initialRouteName="Auth"
        screenOptions={{
          headerTitleAlign: "center",
          headerStyle: { backgroundColor: "#ffffff" },
          headerTintColor: "#111827",
          contentStyle: { backgroundColor: "#F5F5F5" }
        }}
      >
        <Stack.Screen
          name="Auth"
          component={AuthScreen}
          options={{ title: "מלווה לבנייה" }}
        />
        <Stack.Screen
          name="Projects"
          component={ProjectsScreen}
          options={{ title: "הפרויקטים שלי" }}
        />
        <Stack.Screen
          name="StageList"
          component={StageListScreen}
          options={{ title: "שלבי הבנייה" }}
        />
        <Stack.Screen
          name="StageDetail"
          component={StageDetailScreen}
          options={{ title: "פירוט שלב" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

