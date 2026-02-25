import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Pressable,
  TextInput,
  Alert,
  Image
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { NativeStackScreenProps } from "@react-navigation/native-stack";

import { api } from "@src/api/client";
import { ExpandableText } from "@src/components/ExpandableText";
import type { RootStackParamList } from "../../App";

type Props = NativeStackScreenProps<RootStackParamList, "StageDetail">;

type Stage = {
  id: string;
  slug: string;
  title: string;
  short_explanation: string;
  common_mistakes: string;
  must_document: string;
  order_index: number;
};

type CheckItem = {
  id: string;
  title: string;
  description: string | null;
  order_index: number;
  is_done: boolean;
  note: string | null;
  media?: { id: string; url: string }[];
};

type ProjectStageView = {
  project_id: string;
  stage: Stage;
  check_items: CheckItem[];
  media?: { id: string; url: string; caption: string | null }[];
};

type Note = {
  id: string;
  stage_id: string | null;
  body: string;
  created_at: string;
};

export const StageDetailScreen: React.FC<Props> = ({ route }) => {
  const { projectId, stageId } = route.params;
  const [data, setData] = useState<ProjectStageView | null>(null);
  const [loading, setLoading] = useState(false);
  const [checked, setChecked] = useState<Set<string>>(new Set());
  const [itemNotes, setItemNotes] = useState<Record<string, string>>({});
  const [generalNote, setGeneralNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploadingId, setUploadingId] = useState<string | null>(null);
  const [checkItemImages, setCheckItemImages] = useState<
    Record<string, string[]>
  >({});
  const [stageImages, setStageImages] = useState<string[]>([]);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [view, notes] = await Promise.all([
        api.get<ProjectStageView>(`/stages/projects/${projectId}/${stageId}`),
        api.get<Note[]>(`/projects/${projectId}/notes?stage_id=${stageId}`)
      ]);
      setData(view);

      const initiallyChecked = new Set<string>();
      const initialItemNotes: Record<string, string> = {};
      view.check_items.forEach((c) => {
        if (c.is_done) {
          initiallyChecked.add(c.id);
        }
        if (c.note) {
          initialItemNotes[c.id] = c.note;
        }
      });
      setChecked(initiallyChecked);
      setItemNotes(initialItemNotes);

      // תמונות השייכות לשלב (מ‑API) – תומך גם בגרסאות API ישנות בלי media
      setStageImages((view.media ?? []).map((m) => m.url));

      if (notes.length > 0) {
        const sorted = [...notes].sort(
          (a, b) =>
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
        setGeneralNote(sorted[sorted.length - 1]?.body ?? "");
      } else {
        setGeneralNote("");
      }
    } catch (e) {
      console.warn("Failed to load stage or notes", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  if (loading && !data) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  if (!data) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>לא ניתן לטעון את השלב.</Text>
      </View>
    );
  }

  const { stage, check_items } = data;

  const toggleCheck = (id: string) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const saveAll = async () => {
    if (!data) return;
    setSaving(true);
    try {
      const actions: Promise<void>[] = [];

      if (generalNote.trim()) {
        actions.push(
          api.post<void>(`/projects/${data.project_id}/notes`, {
            stage_id: stageId,
            body: generalNote.trim()
          })
        );
      }

      actions.push(
        ...check_items.map((c) => {
          const noteText = (itemNotes[c.id] ?? "").trim();
          const hasSomething = checked.has(c.id) || noteText !== "";
          if (!hasSomething) {
            return Promise.resolve();
          }
          return api.post<void>(`/projects/${data.project_id}/checks/${c.id}`, {
            is_done: checked.has(c.id),
            note: noteText || null
          });
        })
      );

      await Promise.all(actions);
      Alert.alert("נשמר", "ההערות והבדיקות נשמרו בהצלחה לחשבון שלך.");
    } catch (e) {
      console.error("Failed to save notes", e);
      const message =
        e instanceof Error ? e.message : "אירעה שגיאה לא צפויה בשמירה.";
      Alert.alert("שגיאה בשמירה", message);
    } finally {
      setSaving(false);
    }
  };

  const pickAndUploadImage = async (checkItemId: string) => {
    if (!data) return;
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("אין הרשאה", "כדי להוסיף תמונה צריך לאפשר גישה לגלריה.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.7
    });
    if (result.canceled || !result.assets?.length) {
      return;
    }
    const asset = result.assets[0];
    if (!asset.uri) return;

    try {
      // הוספת תצוגה מקומית מידית לבדיקה הזו
      setCheckItemImages((prev) => {
        const current = prev[checkItemId] ?? [];
        return { ...prev, [checkItemId]: [...current, asset.uri] };
      });

      setUploadingId(checkItemId);
      const filename = asset.fileName ?? `check-${checkItemId}.jpg`;
      const contentType = asset.type === "image" ? "image/jpeg" : "application/octet-stream";

      const presigned = await api.post<{
        upload_url: string;
        storage_path: string;
      }>(`/projects/${data.project_id}/media/upload`, {
        stage_id: stageId,
        filename,
        content_type: contentType,
        local_uri: asset.uri
      });

      // במצב פיתוח בלי S3 אמיתי לא מנסים להעלות לשרת חיצוני
      if (!presigned.upload_url.startsWith("DEV_LOCAL://")) {
        const fileRes = await fetch(asset.uri);
        const blob = await fileRes.blob();

        const uploadRes = await fetch(presigned.upload_url, {
          method: "PUT",
          headers: {
            "Content-Type": contentType
          },
          body: blob
        });

        if (!uploadRes.ok) {
          throw new Error("העלאת התמונה נכשלה");
        }
      }

      Alert.alert(
        "העלאה הצליחה",
        "התמונה נוספה לבדיקה זו ותישמר יחד עם ההערות."
      );
    } catch (e) {
      console.error("Failed to upload image", e);
      const message =
        e instanceof Error ? e.message : "אירעה שגיאה בהעלאת התמונה.";
      Alert.alert("שגיאה בהעלאה", message);
    } finally {
      setUploadingId(null);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.title}>{stage.title}</Text>
        <View style={styles.topActionsRow}>
          <Pressable
            onPress={saveAll}
            disabled={saving}
            style={({ pressed }) => [
              styles.topSaveButton,
              (pressed || saving) && { opacity: 0.85 }
            ]}
          >
            <Text style={styles.topSaveButtonText}>
              {saving ? "שומר…" : "שמור את כל השינויים"}
            </Text>
          </Pressable>
        </View>
        <Text style={styles.sectionLabel}>מה כולל שלב זה</Text>
        <ExpandableText text={stage.short_explanation} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>דברים שחייבים לבדוק בשלב זה</Text>
        {check_items.map((c) => (
          <Pressable
            key={c.id}
            style={styles.checkItem}
            onPress={() => toggleCheck(c.id)}
          >
            <View style={styles.checkRow}>
              <View
                style={[
                  styles.checkbox,
                  checked.has(c.id) && styles.checkboxChecked
                ]}
              >
                {checked.has(c.id) && (
                  <Text style={styles.checkboxMark}>✓</Text>
                )}
              </View>
              <Text
                style={[
                  styles.checkTitle,
                  checked.has(c.id) && styles.checkTitleChecked
                ]}
              >
                {c.title}
              </Text>
            </View>
            {c.description ? (
              <Text style={styles.checkDescription}>{c.description}</Text>
            ) : null}
            <TextInput
              style={styles.itemNoteInput}
              placeholder="הערה לפריט זה (אופציונלי)"
              placeholderTextColor="#9CA3AF"
              value={itemNotes[c.id] ?? ""}
              onChangeText={(text) =>
                setItemNotes((prev) => ({ ...prev, [c.id]: text }))
              }
              multiline
              textAlign="right"
            />
            <View style={styles.mediaRow}>
              <Pressable
                style={styles.mediaButton}
                onPress={() => pickAndUploadImage(c.id)}
              >
                <Text style={styles.mediaButtonText}>
                  {uploadingId === c.id ? "מעלה תמונה…" : "הוסף תמונה לבדיקה זו"}
                </Text>
              </Pressable>
              {checkItemImages[c.id]?.length ? (
                <View style={styles.thumbsRow}>
                  {checkItemImages[c.id].map((uri) => (
                    <Image
                      key={uri}
                      source={{ uri }}
                      style={styles.thumb}
                    />
                  ))}
                </View>
              ) : null}
            </View>
          </Pressable>
        ))}
      </View>

      {stageImages.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>תמונות בשלב זה</Text>
          <ScrollView
            horizontal
            contentContainerStyle={styles.stageImagesRow}
            showsHorizontalScrollIndicator={false}
          >
            {stageImages.map((uri) => (
              <Pressable key={uri} onPress={() => setPreviewImage(uri)}>
                <Image source={{ uri }} style={styles.stageImageThumb} />
              </Pressable>
            ))}
          </ScrollView>
        </View>
      )}

      {previewImage && (
        <View style={styles.previewOverlay}>
          <Pressable
            style={styles.previewBackdrop}
            onPress={() => setPreviewImage(null)}
          />
          <View style={styles.previewContent}>
            <Image source={{ uri: previewImage }} style={styles.previewImage} />
            <Pressable
              style={styles.previewCloseButton}
              onPress={() => setPreviewImage(null)}
            >
              <Text style={styles.previewCloseText}>סגור</Text>
            </Pressable>
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>טעויות נפוצות</Text>
        <ExpandableText text={stage.common_mistakes} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>מה חשוב לתעד</Text>
        <ExpandableText text={stage.must_document} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>הערות</Text>
        <TextInput
          style={styles.generalNoteInput}
          placeholder="כתבו כאן דברים חשובים שתרצו לזכור לגבי השלב כולו…"
          placeholderTextColor="#9CA3AF"
          value={generalNote}
          onChangeText={setGeneralNote}
          multiline
          textAlign="right"
        />
        <Text style={styles.muted}>
          הערות אלו נשמרות לחשבון שלך ויקושרו לפרויקט ולשלב הנוכחי.
        </Text>
        <View style={styles.saveButtonWrapper}>
          <Pressable
            onPress={saveAll}
            disabled={saving}
            style={({ pressed }) => [
              styles.saveButton,
              (pressed || saving) && { opacity: 0.85 }
            ]}
          >
            <Text style={styles.saveButtonText}>
              {saving ? "שומר…" : "שמור הערות"}
            </Text>
          </Pressable>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#F5F5F5"
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center"
  },
  errorText: {
    fontSize: 14,
    color: "#B91C1C",
    textAlign: "center"
  },
  title: {
    fontSize: 22,
    fontWeight: "600",
    marginBottom: 8,
    textAlign: "right",
    color: "#111827"
  },
  topActionsRow: {
    flexDirection: "row-reverse",
    justifyContent: "flex-start",
    marginBottom: 4
  },
  topSaveButton: {
    backgroundColor: "#2563EB",
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 6
  },
  topSaveButtonText: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "600"
  },
  section: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#ffffff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 2,
    elevation: 1
  },
  sectionLabel: {
    marginTop: 16,
    marginBottom: 4,
    fontSize: 14,
    fontWeight: "600",
    textAlign: "right",
    color: "#111827"
  },
  body: {
    fontSize: 14,
    color: "#374151",
    textAlign: "right",
    lineHeight: 20
  },
  checkItem: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#E5E7EB"
  },
  checkRow: {
    flexDirection: "row-reverse",
    alignItems: "center"
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: "#D1D5DB",
    alignItems: "center",
    justifyContent: "center",
    marginLeft: 10,
    backgroundColor: "#ffffff"
  },
  checkboxChecked: {
    borderColor: "#2563EB",
    backgroundColor: "#2563EB"
  },
  checkboxMark: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700"
  },
  checkTitle: {
    fontSize: 14,
    fontWeight: "500",
    textAlign: "right",
    color: "#111827"
  },
  checkTitleChecked: {
    textDecorationLine: "line-through",
    color: "#6B7280"
  },
  checkDescription: {
    fontSize: 12,
    color: "#6B7280",
    textAlign: "right",
    marginTop: 2
  },
  itemNoteInput: {
    marginTop: 6,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 8,
    padding: 8,
    backgroundColor: "#F9FAFB",
    fontSize: 12,
    color: "#111827"
  },
  muted: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 4,
    textAlign: "right"
  },
  mediaRow: {
    marginTop: 6,
    flexDirection: "row-reverse",
    alignItems: "center"
  },
  mediaButton: {
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#93C5FD",
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: "#EFF6FF"
  },
  mediaButtonText: {
    fontSize: 12,
    color: "#1D4ED8",
    fontWeight: "500"
  },
  thumbsRow: {
    flexDirection: "row-reverse",
    marginRight: 8
  },
  thumb: {
    width: 40,
    height: 40,
    borderRadius: 6,
    marginLeft: 4
  },
  stageImagesRow: {
    flexDirection: "row-reverse",
    marginTop: 8
  },
  stageImageThumb: {
    width: 80,
    height: 80,
    borderRadius: 10,
    marginLeft: 8
  },
  previewOverlay: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    justifyContent: "center",
    alignItems: "center"
  },
  previewBackdrop: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "rgba(0,0,0,0.5)"
  },
  previewContent: {
    width: "85%",
    borderRadius: 16,
    backgroundColor: "#000",
    padding: 8,
    alignItems: "center"
  },
  previewImage: {
    width: "100%",
    height: 320,
    borderRadius: 12,
    resizeMode: "contain",
    backgroundColor: "#000"
  },
  previewCloseButton: {
    marginTop: 8,
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: "#111827"
  },
  previewCloseText: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "500"
  },
  generalNoteInput: {
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 8,
    padding: 10,
    backgroundColor: "#F9FAFB",
    minHeight: 80,
    fontSize: 14,
    color: "#111827",
    textAlignVertical: "top"
  },
  saveButtonWrapper: {
    marginTop: 10,
    alignItems: "flex-start"
  },
  saveButton: {
    backgroundColor: "#2563EB",
    borderRadius: 999,
    paddingHorizontal: 18,
    paddingVertical: 8
  },
  saveButtonText: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "600"
  }
});

