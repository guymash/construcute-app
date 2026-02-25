import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  Button,
  TextInput,
  StyleSheet
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";

import { api } from "@src/api/client";
import { useAuth } from "@src/store/useAuth";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "Projects">;

type Project = {
  id: string;
  name: string;
  location_text: string | null;
};

export const ProjectsScreen: React.FC<Props> = ({ navigation }) => {
  const token = useAuth((s) => s.token);
  const setToken = useAuth((s) => s.setToken);
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(false);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.get<Project[]>("/projects");
      setProjects(data);
    } catch {
      // ignore for now
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadProjects();
  }, []);

  const onCreate = async () => {
    if (!name.trim()) return;
    try {
      const created = await api.post<Project>("/projects", {
        name: name.trim(),
        location_text: location.trim() || null
      });
      setProjects((prev) => [...prev, created]);
      setName("");
      setLocation("");
    } catch {
      // ignore for now
    }
  };

  const onSwitchUser = () => {
    setToken(null);
    navigation.replace("Auth");
  };

  return (
    <View style={styles.container}>
      <View style={styles.userBar}>
        <View style={{ flex: 1 }}>
          <Text style={styles.userLabel}>משתמש מחובר</Text>
          <Text style={styles.userValue}>
            {token ?? "לא מחובר (לצורכי פיתוח)"}
          </Text>
        </View>
        <Button title="החלפת משתמש" onPress={onSwitchUser} />
      </View>
      <View style={styles.form}>
        <Text style={styles.heading}>פרויקט חדש</Text>
        <TextInput
          style={styles.input}
          placeholder="שם הפרויקט"
          placeholderTextColor="#9CA3AF"
          value={name}
          onChangeText={setName}
          textAlign="right"
        />
        <TextInput
          style={styles.input}
          placeholder="מיקום (אופציונלי)"
          placeholderTextColor="#9CA3AF"
          value={location}
          onChangeText={setLocation}
          textAlign="right"
        />
        <View style={styles.createButtonWrapper}>
          <Button title="צור" onPress={onCreate} />
        </View>
      </View>

      <Text style={styles.heading}>הפרויקטים שלך</Text>
      <FlatList
        data={projects}
        keyExtractor={(item) => item.id}
        refreshing={loading}
        onRefresh={loadProjects}
        renderItem={({ item }) => (
          <View style={styles.projectCard}>
            <View style={styles.projectRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.projectName}>{item.name}</Text>
                {item.location_text ? (
                  <Text style={styles.projectLocation}>
                    {item.location_text}
                  </Text>
                ) : null}
              </View>
              <Button
                title="פתח"
                onPress={() =>
                  navigation.navigate("StageList", { projectId: item.id })
                }
              />
            </View>
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#F5F5F5"
  },
  userBar: {
    flexDirection: "row-reverse",
    alignItems: "center",
    marginBottom: 12
  },
  userLabel: {
    fontSize: 12,
    color: "#6B7280",
    textAlign: "right"
  },
  userValue: {
    fontSize: 14,
    fontWeight: "500",
    color: "#111827",
    textAlign: "right"
  },
  form: {
    marginBottom: 16,
    padding: 16,
    borderRadius: 12,
    backgroundColor: "#ffffff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 2
  },
  heading: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
    textAlign: "right",
    color: "#111827"
  },
  input: {
    borderWidth: 1,
    borderColor: "#cccccc",
    borderRadius: 8,
    padding: 8,
    marginBottom: 8,
    backgroundColor: "#ffffff"
  },
  createButtonWrapper: {
    alignSelf: "flex-end",
    width: "40%",
    marginTop: 4
  },
  projectCard: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 2,
    elevation: 1
  },
  projectRow: {
    flexDirection: "row-reverse",
    alignItems: "center"
  },
  projectName: {
    fontSize: 16,
    fontWeight: "500",
    textAlign: "right",
    color: "#111827"
  },
  projectLocation: {
    fontSize: 12,
    color: "#6B7280",
    textAlign: "right",
    marginTop: 2
  }
});

