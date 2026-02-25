import React, { useEffect, useState } from "react";
import { View, Text, FlatList, Button, StyleSheet } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";

import { api } from "@src/api/client";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "StageList">;

type Stage = {
  id: string;
  slug: string;
  title: string;
  short_explanation: string;
  order_index: number;
};

export const StageListScreen: React.FC<Props> = ({ route, navigation }) => {
  const { projectId } = route.params;
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(false);

  const loadStages = async () => {
    setLoading(true);
    try {
      const data = await api.get<Stage[]>("/stages");
      setStages(data);
    } catch {
      // ignore for now
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadStages();
  }, []);

  return (
    <View style={styles.container}>
      <FlatList
        data={stages}
        keyExtractor={(item) => item.id}
        refreshing={loading}
        onRefresh={loadStages}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.row}>
              <View
                style={{ flex: 1 }}
                // לחיצה על הכרטיס/הטקסט פותחת את השלב
                onStartShouldSetResponder={() => true}
                onResponderRelease={() =>
                  navigation.navigate("StageDetail", {
                    projectId,
                    stageId: item.id
                  })
                }
              >
                <Text style={styles.title}>{item.title}</Text>
                <Text style={styles.explanation}>{item.short_explanation}</Text>
              </View>
              <Button
                title="פתח"
                onPress={() =>
                  navigation.navigate("StageDetail", {
                    projectId,
                    stageId: item.id
                  })
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
  card: {
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
  row: {
    flexDirection: "row-reverse",
    alignItems: "center"
  },
  title: {
    fontSize: 16,
    fontWeight: "500",
    marginBottom: 4,
    textAlign: "right",
    color: "#111827"
  },
  explanation: {
    fontSize: 12,
    color: "#6B7280",
    textAlign: "right"
  }
});

