import React, { useState } from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";

type Props = {
  text: string;
  maxLines?: number;
};

export const ExpandableText: React.FC<Props> = ({ text, maxLines = 3 }) => {
  const [expanded, setExpanded] = useState(false);

  if (!text) {
    return null;
  }

  return (
    <View>
      <Text
        style={styles.body}
        numberOfLines={expanded ? undefined : maxLines}
      >
        {text}
      </Text>
      <Pressable onPress={() => setExpanded((v) => !v)}>
        <Text style={styles.link}>
          {expanded ? "הצג פחות" : "הצג עוד"}
        </Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  body: {
    fontSize: 14,
    color: "#374151",
    textAlign: "right",
    lineHeight: 20
  },
  link: {
    marginTop: 4,
    fontSize: 12,
    color: "#2563EB",
    textAlign: "right",
    fontWeight: "500"
  }
});

