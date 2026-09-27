import React, { useState } from "react";
import {
  View,
  Text,
  Image,
  TextInput,
  Pressable,
  ScrollView,
  Platform,
} from "react-native";
import ProductCard from "./ProductCard";
export default function PlannedCommerce({
  config,
  screen,
  products,
  query,
  setQuery,
  category,
  setCategory,
  onOpen,
  onAdd,
  onNavigate,
  dark,
}) {
  const [width, setWidth] = useState(300);
  const plan = screen.composition;
  const ink = dark ? "#f6f3ff" : "#1a1824",
    muted = dark ? "#b9b2c9" : "#7a708a",
    surface = dark ? "#211c2d" : "#ffffff";
  const rgb = config.primary
    .slice(1)
    .match(/.{2}/g)
    .map((v) => parseInt(v, 16));
  const primaryInk =
    rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114 > 150
      ? "#191522"
      : "#ffffff";
  const radius =
    plan.corners === "sharp" ? 3 : plan.corners === "round" ? 24 : 14;
  const gap =
    plan.density === "airy" ? 22 : plan.density === "compact" ? 8 : 14;
  const headingFont =
    config.font === "serif"
      ? Platform.select({ ios: "Georgia", default: "serif" })
      : undefined;
  const bodyFont =
    config.bodyFont === "serif"
      ? Platform.select({ ios: "Georgia", default: "serif" })
      : undefined;
  const heading = {
    fontSize: 18,
    fontWeight: "700",
    color: ink,
    fontFamily: headingFont,
  };
  const body = {
    fontSize: 12,
    lineHeight: 18,
    color: muted,
    fontFamily: bodyFont,
  };
  const featured = config.products[0];
  const categories = [
    "All",
    ...new Set(config.products.map((p) => p.category).filter(Boolean)),
  ];
  const columns = width >= 1000 ? 4 : width >= 600 ? 3 : 2;
  const button = (
    label,
    action,
    color = primaryInk,
    background = config.primary,
  ) => (
    <Pressable
      accessibilityRole="button"
      onPress={action}
      style={{
        alignSelf: "flex-start",
        minHeight: 40,
        justifyContent: "center",
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderRadius: 8,
        backgroundColor: background,
      }}
    >
      <Text style={{ color, fontWeight: "700", fontSize: 12 }}>{label}</Text>
    </Pressable>
  );
  return (
    <View
      onLayout={(event) => setWidth(event.nativeEvent.layout.width)}
      style={{ gap, width: "100%" }}
    >
      {plan.blocks.map((block, index) => {
        const key = block.kind + "-" + index;
        if (block.kind === "hero") {
          if (screen.show_hero === false) return null;
          const imageHero = plan.hero_style === "image";
          const split = plan.hero_style === "split";
          return (
            <View
              key={key}
              style={{
                borderRadius: radius,
                overflow: "hidden",
                backgroundColor: imageHero ? "#21192b" : config.primary,
                minHeight: imageHero ? 260 : undefined,
                flexDirection: split ? "row" : "column",
                justifyContent: imageHero ? "flex-end" : undefined,
              }}
            >
              {plan.hero_style !== "typographic" && featured?.image_url && (
                <Image
                  source={{ uri: featured.image_url }}
                  resizeMode="cover"
                  style={
                    imageHero
                      ? {
                          position: "absolute",
                          top: 0,
                          left: 0,
                          bottom: 0,
                          right: 0,
                          opacity: 0.48,
                        }
                      : { width: "40%", minHeight: 180 }
                  }
                />
              )}
              <View
                style={{
                  padding: split ? 16 : 22,
                  gap: 14,
                  flex: split ? 1 : undefined,
                }}
              >
                <Text
                  style={{
                    fontSize: 9,
                    letterSpacing: 0.8,
                    color: imageHero ? "white" : primaryInk,
                    fontFamily: bodyFont,
                  }}
                >
                  {block.body || screen.subtitle || "Selected for you"}
                </Text>
                <Text
                  style={{
                    fontSize: split ? 21 : 25,
                    lineHeight: 29,
                    fontWeight: "800",
                    fontFamily: headingFont,
                    color: imageHero ? "white" : primaryInk,
                  }}
                >
                  {block.title || screen.title || "Find your next favourite."}
                </Text>
                {config.pages.includes("products") &&
                  button(
                    "Explore collection →",
                    () => onNavigate("products"),
                    config.primary,
                    primaryInk,
                  )}
              </View>
            </View>
          );
        }
        if (block.kind === "search")
          return screen.show_search !== false ? (
            <TextInput
              key={key}
              accessibilityLabel="Search collection"
              placeholder={block.title || "Search the collection"}
              placeholderTextColor={muted}
              value={query}
              onChangeText={setQuery}
              style={{
                minHeight: 44,
                borderRadius: radius,
                borderWidth: 1,
                borderColor: "#88888844",
                padding: 12,
                backgroundColor: surface,
                color: ink,
                fontSize: 12,
              }}
            />
          ) : null;
        if (block.kind === "categories")
          return (
            <ScrollView
              key={key}
              horizontal
              showsHorizontalScrollIndicator={false}
              style={{ flexGrow: 0 }}
              contentContainerStyle={{ gap: 6 }}
            >
              {categories.map((c) => (
                <Pressable
                  key={c}
                  accessibilityRole="button"
                  onPress={() => setCategory(c)}
                  style={{
                    backgroundColor: category === c ? config.primary : surface,
                    borderRadius: 20,
                    paddingHorizontal: 12,
                    paddingVertical: 10,
                  }}
                >
                  <Text
                    style={{
                      color: category === c ? primaryInk : ink,
                      fontSize: 11,
                    }}
                  >
                    {c}
                  </Text>
                </Pressable>
              ))}
            </ScrollView>
          );
        if (block.kind === "statement")
          return (
            <View
              key={key}
              style={{
                borderTopWidth: 1,
                borderBottomWidth: 1,
                borderColor: "#88888833",
                paddingVertical: 20,
                gap: 6,
              }}
            >
              <Text style={heading}>
                {block.title || "Thoughtfully selected."}
              </Text>
              {!!block.body && <Text style={body}>{block.body}</Text>}
            </View>
          );
        if (block.kind === "spotlight")
          return featured ? (
            <View
              key={key}
              style={{
                flexDirection: "row",
                gap: 14,
                alignItems: "center",
                backgroundColor: surface,
                borderRadius: radius,
                overflow: "hidden",
              }}
            >
              {!!featured.image_url && (
                <Image
                  source={{ uri: featured.image_url }}
                  style={{ width: "43%", height: 170 }}
                  resizeMode="cover"
                />
              )}
              <View
                style={{
                  flex: 1,
                  gap: 8,
                  paddingRight: 10,
                  paddingVertical: 12,
                }}
              >
                <Text style={body}>{block.title || "In focus"}</Text>
                <Text style={heading}>{featured.name}</Text>
                <Text numberOfLines={3} style={body}>
                  {block.body || featured.description}
                </Text>
                {config.pages.includes("detail") &&
                  button(
                    "Discover →",
                    () => onOpen(featured),
                    ink,
                    "transparent",
                  )}
              </View>
            </View>
          ) : null;
        const list = block.layout !== "grid";
        const cardWidth = list
          ? width
          : Math.max(0, (width - (columns - 1) * 12) / columns);
        return (
          <View key={key} style={{ gap: 12 }}>
            <Text style={heading}>
              {block.title || "Explore the collection"}
            </Text>
            {!!block.body && <Text style={body}>{block.body}</Text>}
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
              {products.map((product) => (
                <View key={product.id} style={{ width: cardWidth }}>
                  <ProductCard
                    product={product}
                    primary={config.primary}
                    dark={dark}
                    horizontal={block.layout === "cards"}
                    spacious={width >= 600}
                    imageRatio={plan.image_ratio}
                    cardStyle={plan.card_style}
                    cornerRadius={radius}
                    showBadge={screen.show_badges !== false}
                    onOpen={() => onOpen(product)}
                    onAdd={
                      config.pages.includes("cart")
                        ? () => onAdd(product)
                        : null
                    }
                  />
                </View>
              ))}
            </View>
            {!products.length && (
              <Text style={body}>No products match your search.</Text>
            )}
          </View>
        );
      })}
    </View>
  );
}
