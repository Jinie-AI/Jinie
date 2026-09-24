import React, {useState} from 'react';
import {View, Text, Pressable, Image, StyleSheet} from 'react-native';

export default function ProductCard({product, primary, dark, onOpen, onAdd, horizontal=false, showBadge=true}) {
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

          {Boolean(product.badge && showBadge) && (
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
    padding: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#88888820',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
    marginBottom: 4,
  },
  cardHorizontal: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  art: {
    height: 100,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    position: 'relative',
  },
  artHorizontal: {
    height: 80,
    width: 80,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  badge: {
    position: 'absolute',
    top: 6,
    left: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 8,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  info: {
    marginTop: 6,
  },
  categoryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  category: {
    fontSize: 9,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    fontWeight: '700',
  },
  rating: {
    fontSize: 9,
    color: '#eab308',
    fontWeight: '700',
  },
  name: {
    fontSize: 11,
    fontWeight: '700',
    marginTop: 2,
    lineHeight: 14,
  },
  bottom: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 6,
    paddingTop: 2,
  },
  price: {
    fontSize: 12,
    fontWeight: '800',
  },
  add: {
    width: 22,
    height: 22,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addIcon: {
    color: 'white',
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 16,
  },
});
