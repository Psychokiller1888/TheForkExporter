SEARCH_CUSTOMERS = """
query searchCustomers($args: SearchCustomersInput!) {
  searchCustomers(input: $args) {
    results {
      highlight {
        firstName {
          offset
          length
          __typename
        }
        lastName {
          offset
          length
          __typename
        }
        __typename
      }
      customer {
        id
        firstName
        lastName
        email
        phone
        secondaryPhone
        status
        isPromoter
        isVip
        rank
        computedRank
        allergiesAndIntolerances
        dietaryRestrictions
        __typename
      }
      reservation {
        id
        mealDate
        creationDate
        pax
        status
        isOnline
        bookingOrigin
        restaurant {
          restaurantUuid
          name
          __typename
        }
        __typename
      }
      __typename
    }
    pageInfo {
      totalCount
      offset
      __typename
    }
    __typename
  }
}
"""

GET_CUSTOMER = """
query getCustomerForCard($id: ID!) {
  customer(id: $id) {
    id
    civility
    firstName
    lastName
    email
    phone
    secondaryPhone
    locale
    notes
    optin
    restaurantOptin {
      isActive
      status
      updatedAt
      __typename
    }
    allergiesAndIntolerances
    status
    isPromoter
    ...customerForList
    __typename
  }
}

fragment customerForList on Customer {
  id
  civility
  firstName
  lastName
  status
  email
  phone
  secondaryPhone
  locale
  notes
  rank
  computedRank
  isVip
  allergiesAndIntolerances
  isPromoter
  dietaryRestrictions
  bookingCount
  customerReliabilityScore
  recentNoShowCount
  recentBookingCount
  favFood
  favDrinks
  favSeating
  birthDate
  address
  customFieldValues
  customFieldLabels
  __typename
}
"""

GET_CUSTOMER_STATS = """
query getCustomerStatsForReservationForm($id: ID!, $restaurantUuid: ID!, $withSpending: Boolean!) {
  customer(id: $id) {
    id
    reservationStats(restaurantUuid: $restaurantUuid) {
      reservationRecordedCount
      reservationCanceledCount
      reservationNoShowCount
      reservationRecordedCountForGroup
      reservationCanceledCountForGroup
      reservationNoShowCountForGroup
      __typename
    }
    posSpending(restaurantUuid: $restaurantUuid) @include(if: $withSpending) {
      amount
      currency
      __typename
    }
    __typename
  }
}
"""