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

GET_CUSTOMER_HISTORY = """
query GetCustomerHistory($restaurantId: String!, $customerId: String!, $onGroup: Boolean, $orderBy: CustomerReservationOrderByInput) {
  customerReservations(
    restaurantUuid: $restaurantId
    customerUuid: $customerId
    onGroup: $onGroup
    orderBy: $orderBy
  ) {
    id
    isOnline
    bookingOrigin
    mealDate
    status
    partySize
    tableName
    customerNote
    restaurantNote
    occasions
    tables {
      isLocked
      items {
        id
        name
        __typename
      }
      __typename
    }
    promoter {
      id
      __typename
    }
    customer {
      id
      firstName
      lastName
      status
      __typename
    }
    offerSnapshot {
      descriptionTags
      discountPercentage
      __typename
    }
    menu {
      menuUuid
      __typename
    }
    order {
      totalPrice
      currencyIso
      orderLines {
        label
        __typename
      }
      __typename
    }
    isBurningYums
    imprint {
      id
      __typename
    }
    restaurantUuid
    restaurant {
      restaurantUuid
      name
      __typename
    }
    review {
      id
      rating
      comment
      createdTs
      __typename
    }
    __typename
  }
}
"""