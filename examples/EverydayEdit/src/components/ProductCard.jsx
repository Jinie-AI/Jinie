import React, {useState} from 'react';
import {View, Text, Pressable, Image, StyleSheet} from 'react-native';

export default function ProductCard({product, primary, dark, onOpen, onAdd, horizontal=false}) {
  const [imgError, setImgError] = useState(false);
  const showImage = Boolean(product?.image_url && !imgError);

  return (
    <View style={[styles.card, {backgroundColor: dark ? '#211c2d' : '#ffffff'}, horizontal && styles.cardHorizontal]}>
      <Pressable accessibilityRole="button" accessibilityLabel={'View ' + product.name} onPress={onOpen}>
        <View style={[styles.art, horizontal && styles.artHorizontal, {backgroundColor: dark ? '#2c253b' : '#f4effa'}]}>
          {showImage ? (
            <Image
              source={{uri: product.image_url}}
              style={styles.image}
              resizeMode="cover"
              onError={() => setImgError(true)}
            />
          ) : (
            <Text style={{fontSize: horizontal ? 42 : 54}}>{product.icon || '✦'}</Text>
          )}

          {Boolean(product.badge) && (
            <View style={[styles.badge, {backgroundColor: primary}]}>
              <Text style={styles.badgeText}>{product.badge}</Text>
            </View>
          )}
        </View>

        <View style={styles.info}>
          <View style={styles.categoryRow}>
            <Text style={[styles.category, {color: dark ? '#b9b2c9' : '#7d748c'}]}>
              {product.category || 'Collection'}
            </Text>
            {Boolean(product.rating) && (
              <Text style={styles.rating}>★ {product.rating}</Text>
            )}
          </View>
          <Text numberOfLines={2} style={[styles.name, {color: dark ? '#f6f3ff' : '#221d32'}]}>
            {product.name}
          </Text>
        </View>
      </Pressable>

      <View style={styles.bottom}>
        <Text style={[styles.price, {color: primary}]}>
          Rs. {product.price.toLocaleString()}
        </Text>
        {onAdd && (
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={'Add ' + product.name + ' to bag'}
            onPress={onAdd}
            style={[styles.add, {backgroundColor: primary}]}
          >
            <Text style={styles.addIcon}>+</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#88888820',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.08,
    shadowRadius: 10,
    elevation: 3,
    marginBottom: 4,
  },
  cardHorizontal: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  art: {
    height: 140,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    position: 'relative',
  },
  artHorizontal: {
    height: 90,
    width: 105,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  badge: {
    position: 'absolute',
    top: 8,
    left: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  info: {
    marginTop: 10,
  },
  categoryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  category: {
    fontSize: 10,
    letterSpacing: 1,
    textTransform: 'uppercase',
    fontWeight: '600',
  },
  rating: {
    fontSize: 11,
    color: '#eab308',
    fontWeight: '700',
  },
  name: {
    fontSize: 14,
    fontWeight: '700',
    marginTop: 4,
    lineHeight: 18,
    minHeight: 36,
  },
  bottom: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 10,
    paddingTop: 6,
  },
  price: {
    fontSize: 15,
    fontWeight: '800',
  },
  add: {
    width: 34,
    height: 34,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addIcon: {
    color: 'white',
    fontSize: 20,
    fontWeight: '700',
    lineHeight: 22,
  },
});
