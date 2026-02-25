import React, { useState } from "react";
import { View, Text, TextInput, Button, StyleSheet } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";

import { useAuth } from "@src/store/useAuth";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "Auth">;

export const AuthScreen: React.FC<Props> = ({ navigation }) => {
  const [userId, setUserId] = useState("");
  const setToken = useAuth((s) => s.setToken);

  const onContinue = () => {
    if (!userId.trim()) {
      return;
    }
    setToken(userId.trim());
    navigation.replace("Projects");
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>מלווה לבניית בית</Text>
      <Text style={styles.subtitle}>
        הכניסו מזהה קצר כדי להתחיל (לצורכי פיתוח בלבד).
      </Text>
      <TextInput
        style={styles.input}
        placeholder="מזהה משתמש"
        placeholderTextColor="#9CA3AF"
        value={userId}
        onChangeText={setUserId}
        autoCapitalize="none"
        textAlign="right"
      />
      <View style={styles.buttonWrapper}>
        <Button title="המשך" onPress={onContinue} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: 24,
    backgroundColor: "#F5F5F5"
  },
  title: {
    fontSize: 24,
    fontWeight: "600",
    marginBottom: 8,
    textAlign: "right",
    color: "#111827"
  },
  subtitle: {
    fontSize: 14,
    color: "#4B5563",
    marginBottom: 16,
    textAlign: "right"
  },
  input: {
    borderWidth: 1,
    borderColor: "#cccccc",
    borderRadius: 8,
    padding: 10,
    marginBottom: 16,
    backgroundColor: "#ffffff"
  },
  buttonWrapper: {
    alignSelf: "flex-end",
    width: "40%"
  }
});

